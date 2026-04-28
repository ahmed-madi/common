import secrets
import urllib.parse

import frappe
from frappe.utils import get_url
from frappe.utils.oauth import get_info_via_oauth

from common.api.utils.jwt import prepare_token
from common.api.utils.response import build_success_response, build_error_response


# ---------------------------------------------------------------------------
# Provider helpers  (used only by get_oauth_url to build the authorization URL)
# ---------------------------------------------------------------------------

def _match(provider_name, *keywords):
    name = provider_name.lower()
    return any(kw in name for kw in keywords)


def _is_microsoft(name):
    return _match(name, "microsoft", "office 365", "office_365", "office365", "azure", "entra")


def _is_google(name):
    return _match(name, "google")


def _is_facebook(name):
    return _match(name, "facebook", "meta")


def _get_authorize_url(slk):
    """Return the authorization endpoint, preferring the configured field."""
    if slk.authorize_url:
        return slk.authorize_url
    name = slk.provider_name
    if _is_microsoft(name):
        tenant = getattr(slk, "tenant_id", None) or "common"
        return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
    if _is_google(name):
        return "https://accounts.google.com/o/oauth2/v2/auth"
    if _is_facebook(name):
        return "https://www.facebook.com/v12.0/dialog/oauth"
    return slk.base_url or None


def _get_scope(slk):
    """Return OAuth scopes, preferring the configured field."""
    if slk.scope:
        return slk.scope
    name = slk.provider_name
    if _is_microsoft(name):
        return "openid profile email User.Read"
    if _is_facebook(name):
        return "email public_profile"
    return "openid profile email"


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
            fields=["name", "provider_name", "icon"],
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
def get_oauth_url(provider):
    """
    Generate an OAuth 2.0 authorization URL for the given Social Login Key name.
    The mobile app opens this URL in a browser/webview, then calls /callback
    with the authorization code it receives.
    """
    try:
        slk = frappe.get_doc("Social Login Key", provider)

        if not slk.enable_social_login:
            return build_error_response(400, f"Social login is not enabled for {provider}", "Provider not enabled")

        auth_url = _get_authorize_url(slk)
        if not auth_url:
            return build_error_response(
                400,
                f"Authorization URL not configured for provider '{provider}'",
                "Set the 'Authorize URL' field on the Social Login Key",
            )

        state = secrets.token_urlsafe(32)
        frappe.cache().set_value(
            f"oauth_state_{state}",
            {"provider": provider, "timestamp": frappe.utils.now()},
            expires_in_sec=600,
        )

        redirect_uri = "/api/method/common.api.controllers.user.social_login.handle_oauth_callback"
        params = {
            "client_id": slk.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": _get_scope(slk),
            "state": state,
        }

        if _is_microsoft(slk.provider_name):
            params["response_mode"] = "query"

        authorization_url = f"{auth_url}?{urllib.parse.urlencode(params)}"

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
def handle_oauth_callback(code, state, provider=None):
    """
    Exchange an OAuth authorization code for app JWT tokens.

    Uses frappe.utils.oauth.get_info_via_oauth to handle the token exchange
    and user-info fetch (the same utility Frappe's own login_via_oauth2 /
    login_via_oauth2_id_token uses internally).  We skip login_oauth_user —
    which would create a cookie-based web session — and issue JWT tokens
    instead.
    """
    try:
        # --- CSRF validation ---
        cached_state = frappe.cache().get_value(f"oauth_state_{state}")
        if not cached_state:
            return build_error_response(400, "Invalid or expired state token", "CSRF validation failed")

        provider = provider or cached_state.get("provider")
        frappe.cache().delete_value(f"oauth_state_{state}")  # one-time use

        slk = frappe.get_doc("Social Login Key", provider)

        # --- Use Frappe's OAuth utility for token exchange + user-info ---
        # id_token=True for Microsoft/Office 365: the email lives in the JWT
        # id_token returned by the token endpoint, no Graph API call needed.
        use_id_token = _is_microsoft(slk.provider_name)
        info = get_info_via_oauth(provider, code, id_token=use_id_token)

        email = info.get("email")
        if not email:
            return build_error_response(400, "Email not provided by OAuth provider", "Email is required for login")

        # --- Validate user ---
        user = frappe.db.exists("User", email)
        if not user:
            frappe.log_error(
                title="Social Login Failed - User Not Found",
                message=f"No Frappe user for email {email} (provider: {provider})",
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
                    message=f"User {user} authenticated via {provider} but has no employee record",
                )
                return build_error_response(409, "Invalid employee account", "No employee record found for this user")

        # --- Issue JWT tokens (no Frappe session created) ---
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
            message=f"Error handling OAuth callback: {str(e)}\n\n{frappe.get_traceback()}",
        )
        return build_error_response(500, "Failed to complete social login", str(e))
