import frappe
from frappe.utils import get_url

from common.api.controllers.user.social_login import _exchange_code_for_user_info, _get_email
from common.api.utils.jwt import prepare_token
from common.api.utils.response import build_success_response, build_error_response


@frappe.whitelist(allow_guest=True)
def login_via_office365(code: str, state: str):
    cached = frappe.cache().get_value(f"oauth_state_{state}")

    if not cached:
        # Login was not initiated via our API — fall back to Frappe's standard flow.
        from frappe.utils.oauth import login_via_oauth2_id_token
        from frappe.integrations.oauth2_logins import decoder_compat
        return login_via_oauth2_id_token("office_365", code, state, decoder=decoder_compat)

    provider = cached["provider"]
    redirect_uri = cached["redirect_uri"]
    success_redirect_url = cached.get("success_redirect_url")
    frappe.cache().delete_value(f"oauth_state_{state}")

    try:
        info = _exchange_code_for_user_info(provider, code, redirect_uri)
    except Exception as e:
        frappe.log_error(title="Office365 Token Exchange Failed", message=f"{str(e)}\n\n{frappe.get_traceback()}")
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
        import urllib.parse
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
