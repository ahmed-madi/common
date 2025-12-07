import frappe
from frappe import _
from frappe.auth import LoginManager, MAX_PASSWORD_SIZE
from frappe.utils import now_datetime, cint, today
from frappe.core.doctype.user.user import (
    test_password_strength,
    reset_user_data,
)
from frappe.utils.password import update_password as _update_password
from common.api.utils.jwt import prepare_token
from common.api.utils.response import build_success_response, build_error_response
from common.api.utils import (
    get_token_from_header,
    get_request_form_data,
    handle_password_test_fail,
)

LOGOUT_FROM_ALL = True

@frappe.whitelist(allow_guest=True)
def login(username: str, password: str):
    """
    Authenticate user and return access/refresh tokens.
    
    Args:
        username: User's email, username, or user ID
        password: User's password
        
    Returns:
        Success response with user data and tokens, or error response
    """
    try:
        login_manager = LoginManager()
        password = str(password)
        
        # check by name
        user = frappe.db.exists("User", username)
        if not user:
            # check by email
            user = frappe.db.get_value(
                "User", {"email": username}, "name", as_dict=True
            )
        if not user:
            # check by user name
            user = frappe.db.get_value(
                "User", {"username": username}, "name", as_dict=True
            )
        if not user:
            frappe.throw("Invalid username or password", frappe.AuthenticationError)
        
        login_manager.authenticate(user, password)
        
        if (
            user != "Administrator"
            and frappe.db.get_value("Employee", {"user_id": user}, "name") is None
        ):
            frappe.throw(msg="Employee not found", exc=frappe.NotFound)

        user = frappe.get_doc("User", user)
        tokens = prepare_token(user)
        frappe.db.commit()
        
        data = frappe._dict()
        data.update(
            {
                "user": user.name,
                "email": user.email,
                "language": user.language,
                "full_name": user.full_name,
            }
        )
        data.update(tokens)
        
        return build_success_response(
            status_code=200, 
            message="Login successful", 
            data=data
        )
        
    except frappe.NotFound:
        frappe.log_error(
            title="Login Failed - Employee Not Found",
            message=f"User {username} exists but has no employee record"
        )
        return build_error_response(
            status_code=409,
            message="Invalid employee account",
            error="Invalid credentials",
        )
        
    except frappe.AuthenticationError:
        frappe.log_error(
            title="Login Failed - Authentication Error",
            message=f"Authentication failed for user {username}"
        )
        return build_error_response(
            status_code=401,
            message="Invalid username or password",
            error="Invalid credentials",
        )
        
    except Exception as e:
        # Catch any other unexpected errors
        frappe.log_error(
            title="Login Failed - Unexpected Error",
            message=f"Error during login for user {username}: {str(e)}\n\n{frappe.get_traceback()}"
        )
        return build_error_response(
            status_code=500,
            message="An error occurred during login",
            error=str(e),
        )



@frappe.whitelist(allow_guest=True)
def refresh_token(refresh_token="", user=""):
    user = frappe.db.exists("User", user)
    if not user:
        return build_error_response(
            status_code=401,
            message="Invalid or expired refresh token",
            error="Invalid or expired refresh token",
        )
    now = now_datetime()
    refresh_token_doc = frappe.db.get_value(
        "HR Auth Refresh Token",
        {
            "refresh_token": refresh_token,
            "user": user,
            "status": "Active",
            "expiration_time": (">", now),
        },
        "name",
    )
    if not refresh_token_doc:
        return build_error_response(
            status_code=401,
            message="Invalid or expired refresh token",
            error="Invalid or expired refresh token",
        )

    refresh_token_doc = frappe.get_doc("HR Auth Refresh Token", refresh_token_doc)
    user = frappe.get_doc("User", refresh_token_doc.user)
    tokens = prepare_token(user)
    # refresh_token_doc.status = "Revoked"
    # refresh_token_doc.save(ignore_permissions=True)
    frappe.db.commit()
    data = frappe._dict()
    data.update(
        {
            "user": user.name,
            "email": user.email,
            "language": user.language,
            "full_name": user.full_name,
        }
    )
    data.update(tokens)
    build_success_response(
        status_code=200, message="New access token generated successfully", data=data
    )


@frappe.whitelist()
def logout():
    if LOGOUT_FROM_ALL:
        frappe.db.sql(
            """
                UPDATE `tabHR Auth Access Token`
                SET status='Revoked'
                WHERE user=%s
            """,
            frappe.session.user,
        )
        frappe.db.sql(
            """
                UPDATE `tabHR Auth Refresh Token`
                SET status='Revoked'
                WHERE user=%s
            """,
            frappe.session.user,
        )
    else:
        token = get_token_from_header()
        frappe.db.sql(
            """
                UPDATE `tabHR Auth Access Token`
                SET status='Revoked'
                WHERE access_token=%s
            """,
            token,
        )
        frappe.db.sql(
            """
                UPDATE `tabHR Auth Refresh Token`
                SET status='Revoked'
                WHERE access_token=%s
            """,
            token,
        )
    frappe.db.commit()
    build_success_response(
        status_code=200, message="Logged out successfully", data=None
    )


@frappe.whitelist()
def change_user_password():
    try:
        data = get_request_form_data()
        new_password = data.get("new_password", None)
        logout_all_sessions = data.get("logout_all_sessions", 0)
        if not new_password or new_password is None:
            return build_error_response(
                403, "Failed to update password", "Provide password please"
            )
        if len(new_password) > MAX_PASSWORD_SIZE:
            frappe.throw(_("Password size exceeded the maximum allowed size."))

        result = test_password_strength(new_password)
        feedback = result.get("feedback", None)

        if feedback and not feedback.get("password_policy_validation_passed", False):
            msg = handle_password_test_fail(feedback)
            return build_error_response(403, "Failed to update password", msg)

        logout_all_sessions = cint(logout_all_sessions) or frappe.db.get_single_value(
            "System Settings", "logout_on_password_reset"
        )
        user = frappe.session.user
        _update_password(
            user, new_password, logout_all_sessions=cint(logout_all_sessions)
        )
        user_doc, redirect_url = reset_user_data(user)
        user_doc.validate_reset_password()

        frappe.local.login_manager.login_as(user)

        frappe.db.set_value("User", user, "last_password_reset_date", today())
        frappe.db.set_value("User", user, "reset_password_key", "")
        user = frappe.get_doc("User", user)
        data = {
            "name": user.name,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
        }
        build_success_response(status_code=200, message="Password Updated", data=data)
    except:  # noqa: E722
        build_error_response(403, "Failed to update password", frappe.get_traceback())
