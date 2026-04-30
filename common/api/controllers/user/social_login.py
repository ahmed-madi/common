import json
import secrets
import urllib.parse

import frappe
from frappe.utils import get_url
from frappe.utils.oauth import get_oauth2_flow, get_oauth2_providers, build_oauth_url

from common.api.utils.jwt import prepare_token
from common.api.utils.response import build_success_response, build_error_response


# Path to this module's callback — used as the redirect_uri in every OAuth flow.
# Must be registered as an allowed redirect in each OAuth provider's app settings.
_CALLBACK_PATH = "/api/method/common.api.controllers.user.social_login.handle_oauth_callback"


def _decoder_compat(b):
    if isinstance(b, bytes):
        return json.loads(b.decode("utf-8"))
    return json.loads(b)


def _is_microsoft(provider_name: str) -> bool:
    name = provider_name.lower()
    return any(kw in name for kw in ("microsoft", "office 365", "office_365", "office365", "azure", "entra"))


def _get_scope(slk) -> str:
    """Extract scope from Social Login Key's auth_url_data, with sane defaults."""
    if slk.get("auth_url_data"):
        try:
            data = json.loads(slk.auth_url_data)
            if "scope" in data:
                return data["scope"]
        except (json.JSONDecodeError, TypeError):
            pass

    if _is_microsoft(slk.provider_name):
        return "openid profile email User.Read"
    return "openid profile email"


def _get_email(info: dict) -> str:
    """Extract email from the user-info dict, handling provider-specific field names."""
    return (info.get("email") or info.get("upn") or info.get("unique_name") or "").lower()


def _exchange_code_for_user_info(provider: str, code: str, redirect_uri: str) -> dict:
    """
    Exchange an OAuth authorization code for user info.

    Mirrors Frappe's get_info_via_oauth but accepts redirect_uri explicitly so it
    matches the URI we sent in the authorization request (our mobile callback), not
    the one stored in the Social Login Key document (Frappe's web callback).
    """
    import jwt as pyjwt

    flow = get_oauth2_flow(provider)
    oauth2_providers = get_oauth2_providers()

    session = flow.get_auth_session(
        data={
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        decoder=_decoder_compat,
    )

    slk = frappe.get_cached_doc("Social Login Key", provider)

    if _is_microsoft(slk.provider_name):
        # Microsoft returns the user's email inside the id_token JWT — no extra API call needed.
        parsed = json.loads(session.access_token_response.text)
        info = pyjwt.decode(parsed["id_token"], options={"verify_signature": False})
    else:
        api_endpoint = oauth2_providers[provider].get("api_endpoint")
        api_endpoint_args = oauth2_providers[provider].get("api_endpoint_args")
        info = session.get(api_endpoint, params=api_endpoint_args).json()

    return info


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_providers():
    """Return all enabled Social Login Key providers."""
    try:
        providers = frappe.get_all(
            "Social Login Key",
            filters={"enable_social_login": 1},
            fields=["name", "provider_name", "icon", "custom_color as color"],
        )
        return build_success_response(
            status_code=200,
            message="Social login providers retrieved successfully",
            data={"providers": providers},
        )
    except Exception as e:
        frappe.log_error(title="Get Social Providers Failed", message=f"{str(e)}\n\n{frappe.get_traceback()}")
        return build_error_response(500, "Failed to retrieve social login providers", str(e))


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_oauth_url(provider: str):
    """
    Generate an OAuth 2.0 authorization URL for the given Social Login Key name.

    The mobile app opens this URL in a browser/webview. After the user authenticates,
    the provider redirects to handle_oauth_callback with `code` and `state` parameters.
    """
    try:
        slk = frappe.get_doc("Social Login Key", provider)

        if not slk.enable_social_login:
            return build_error_response(400, f"Social login is not enabled for '{provider}'", "Provider not enabled")

        if not slk.authorize_url:
            return build_error_response(
                400,
                f"Authorization URL not configured for provider '{provider}'",
                "Set the 'Authorize URL' field on the Social Login Key",
            )

        # Prefer the redirect_url configured on the Social Login Key (registered with the
        # OAuth provider, supports mobile deep links like myapp://oauth/callback).
        # Fall back to our server-side callback only when none is configured.
        if slk.redirect_url:
            _parsed = urllib.parse.urlparse(slk.redirect_url)
            redirect_uri = (
                slk.redirect_url if (_parsed.scheme and _parsed.netloc) else get_url(slk.redirect_url)
            )
        else:
            redirect_uri = get_url(_CALLBACK_PATH)

        state = secrets.token_urlsafe(32)

        # Store provider + redirect_uri so handle_oauth_callback can use them without
        # re-deriving, and so the redirect_uri passed to the token exchange is identical.
        frappe.cache().set_value(
            f"oauth_state_{state}",
            {"provider": provider, "redirect_uri": redirect_uri, "timestamp": frappe.utils.now()},
            expires_in_sec=600,
        )

        params = {
            "client_id": slk.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": _get_scope(slk),
            "state": state,
        }

        # Merge any additional auth_url_data params from the Social Login Key
        # (e.g. response_type overrides, extra scopes), without overwriting our params.
        if slk.get("auth_url_data"):
            try:
                for k, v in json.loads(slk.auth_url_data).items():
                    if k not in params:
                        params[k] = v
            except (json.JSONDecodeError, TypeError):
                pass

        if _is_microsoft(slk.provider_name):
            params["response_mode"] = "query"

        # For providers with custom_base_url (e.g. Keycloak, self-hosted Frappe),
        # resolve the authorize_url relative to base_url.
        authorize_url = build_oauth_url(slk.base_url, slk.authorize_url) if slk.custom_base_url else slk.authorize_url

        authorization_url = f"{authorize_url}?{urllib.parse.urlencode(params)}"

        return build_success_response(
            status_code=200,
            message="OAuth URL generated successfully",
            data={
                "authorization_url": authorization_url,
                "state": state,
                "provider": provider,
                "redirect_uri": redirect_uri,
            },
        )

    except frappe.DoesNotExistError:
        return build_error_response(404, f"Social login provider '{provider}' not found", "Provider not configured")
    except Exception as e:
        frappe.log_error(
            title="Get OAuth URL Failed",
            message=f"Error generating OAuth URL for {provider}: {str(e)}\n\n{frappe.get_traceback()}",
        )
        return build_error_response(500, "Failed to generate OAuth URL", str(e))


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
def handle_oauth_callback(code: str, state: str, provider: str = None):
    """
    Exchange an OAuth authorization code for app JWT tokens.

    Called by the mobile app (or by the provider's redirect) after the user completes
    OAuth login. Validates the CSRF state, exchanges the code for user info using the
    same redirect_uri that was sent in the authorization request, then returns JWT tokens.
    """
    try:
        # --- CSRF / state validation ---
        cached = frappe.cache().get_value(f"oauth_state_{state}")
        if not cached:
            return build_error_response(400, "Invalid or expired state token", "CSRF validation failed")

        provider = provider or cached.get("provider")
        redirect_uri = cached.get("redirect_uri") or get_url(_CALLBACK_PATH)
        frappe.cache().delete_value(f"oauth_state_{state}")  # one-time use

        # --- Token exchange + user-info fetch ---
        info = _exchange_code_for_user_info(provider, code, redirect_uri)

        email = _get_email(info)
        if not email:
            return build_error_response(400, "Email not provided by OAuth provider", "Email is required for login")

        # --- Verify user exists and is active ---
        user = frappe.db.exists("User", email)
        if not user:
            frappe.log_error(
                title="Social Login Failed - User Not Found",
                message=f"No Frappe user for email '{email}' (provider: {provider})",
            )
            return build_error_response(404, "User account not found. Please contact your administrator.", "User does not exist")

        user_doc = frappe.get_doc("User", user)

        if not user_doc.enabled:
            return build_error_response(403, "User account is disabled", "Account disabled")

        if user != "Administrator":
            employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
            if not employee:
                frappe.log_error(
                    title="Social Login Failed - Employee Not Found",
                    message=f"User '{user}' authenticated via {provider} but has no employee record",
                )
                return build_error_response(409, "Invalid employee account", "No employee record found for this user")

        # --- Issue JWT tokens (no Frappe web session created) ---
        tokens = prepare_token(user_doc)
        frappe.db.commit()

        return build_success_response(
            status_code=200,
            message="Login successful",
            data={
                "user": user_doc.name,
                "email": user_doc.email,
                "language": user_doc.language,
                "full_name": user_doc.full_name,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
            },
        )

    except frappe.DoesNotExistError:
        return build_error_response(404, f"Social login provider '{provider}' not found", "Provider not configured")
    except Exception as e:
        frappe.log_error(
            title="OAuth Callback Failed",
            message=f"Error handling OAuth callback for provider '{provider}': {str(e)}\n\n{frappe.get_traceback()}",
        )
        return build_error_response(500, "Failed to complete social login", str(e))
