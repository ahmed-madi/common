import frappe

from common.api.controllers.user.social_login import _exchange_code_for_user_info, _get_email
from common.api.utils.jwt import prepare_token
from common.api.utils.response import build_success_response, build_error_response


def _our_jwt_flow(cached: dict, code: str):
    """Issue JWT tokens and redirect (or return JSON) after a successful OAuth exchange."""
    import urllib.parse

    provider = cached["provider"]
    redirect_uri = cached["redirect_uri"]
    success_redirect_url = cached.get("success_redirect_url")

    try:
        info = _exchange_code_for_user_info(provider, code, redirect_uri)
    except Exception as e:
        frappe.log_error(title="Social Login Token Exchange Failed", message=f"{str(e)}\n\n{frappe.get_traceback()}")
        return build_error_response(500, "Failed to exchange authorization code", str(e))

    email = _get_email(info)
    if not email:
        return build_error_response(400, "Email not provided by OAuth provider", "Email is required for login")

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

    tokens = prepare_token(user_doc)
    frappe.db.commit()

    if success_redirect_url:
        fragment = urllib.parse.urlencode({
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "user": user_doc.name,
            "email": user_doc.email,
            "full_name": user_doc.full_name,
        })
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"{success_redirect_url}#{fragment}"
        return

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


def _handle_callback(code: str, state: str, frappe_fallback):
    """
    Central dispatcher for all provider callback overrides.

    If the state is in our Redis cache the login was initiated via our API →
    run our JWT flow. Otherwise fall back to Frappe's original handler so that
    Frappe's own web-based social login keeps working.
    """
    cached = frappe.cache().get_value(f"oauth_state_{state}")
    if not cached:
        return frappe_fallback()

    frappe.cache().delete_value(f"oauth_state_{state}")
    return _our_jwt_flow(cached, code)


# ---------------------------------------------------------------------------
# One override per Frappe built-in handler, each delegating to _handle_callback.
# The fallback lambda calls Frappe's original function directly (not the override)
# to avoid infinite recursion.
# ---------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def login_via_google(code: str, state: str):
    from frappe.utils.oauth import login_via_oauth2
    from frappe.integrations.oauth2_logins import decoder_compat
    return _handle_callback(code, state,
        lambda: login_via_oauth2("google", code, state, decoder=decoder_compat))


@frappe.whitelist(allow_guest=True)
def login_via_github(code: str, state: str):
    from frappe.utils.oauth import login_via_oauth2
    return _handle_callback(code, state,
        lambda: login_via_oauth2("github", code, state))


@frappe.whitelist(allow_guest=True)
def login_via_facebook(code: str, state: str):
    from frappe.utils.oauth import login_via_oauth2
    from frappe.integrations.oauth2_logins import decoder_compat
    return _handle_callback(code, state,
        lambda: login_via_oauth2("facebook", code, state, decoder=decoder_compat))


@frappe.whitelist(allow_guest=True)
def login_via_frappe(code: str, state: str):
    from frappe.utils.oauth import login_via_oauth2
    from frappe.integrations.oauth2_logins import decoder_compat
    return _handle_callback(code, state,
        lambda: login_via_oauth2("frappe", code, state, decoder=decoder_compat))


@frappe.whitelist(allow_guest=True)
def login_via_office365(code: str, state: str):
    from frappe.utils.oauth import login_via_oauth2_id_token
    from frappe.integrations.oauth2_logins import decoder_compat
    return _handle_callback(code, state,
        lambda: login_via_oauth2_id_token("office_365", code, state, decoder=decoder_compat))


@frappe.whitelist(allow_guest=True)
def login_via_salesforce(code: str, state: str):
    from frappe.utils.oauth import login_via_oauth2
    from frappe.integrations.oauth2_logins import decoder_compat
    return _handle_callback(code, state,
        lambda: login_via_oauth2("salesforce", code, state, decoder=decoder_compat))


@frappe.whitelist(allow_guest=True)
def login_via_fairlogin(code: str, state: str):
    from frappe.utils.oauth import login_via_oauth2
    from frappe.integrations.oauth2_logins import decoder_compat
    return _handle_callback(code, state,
        lambda: login_via_oauth2("fairlogin", code, state, decoder=decoder_compat))


@frappe.whitelist(allow_guest=True)
def login_via_keycloak(code: str, state: str):
    from frappe.utils.oauth import login_via_oauth2
    from frappe.integrations.oauth2_logins import decoder_compat
    return _handle_callback(code, state,
        lambda: login_via_oauth2("keycloak", code, state, decoder=decoder_compat))


@frappe.whitelist(allow_guest=True)
def custom(code: str, state: str):
    """Override for user-added providers routed via /api/method/frappe.integrations.oauth2_logins.custom/<provider>."""
    from frappe.utils.oauth import login_via_oauth2
    from frappe.integrations.oauth2_logins import decoder_compat

    def frappe_fallback():
        path = frappe.request.path[1:].split("/")
        if len(path) == 4 and path[3] and frappe.db.exists("Social Login Key", path[3]):
            login_via_oauth2(path[3], code, state, decoder=decoder_compat)

    return _handle_callback(code, state, frappe_fallback)
