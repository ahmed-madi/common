import frappe
from frappe.auth import LoginManager
from frappe.utils import now_datetime
from common.api.utils.jwt import prepare_token
from common.api.utils.response import build_success_response, build_error_response
from common.api.utils import get_token_from_header
from common.utils.hr import get_employee_from_user

LOGOUT_FROM_ALL = True

@frappe.whitelist(allow_guest=True)
def login(username: str, password: str):
    login_manager = LoginManager()
    password = str(password)
    try:
        # check by name
        user = frappe.db.exists("User", username)
        if not user:
            # check by email
            user = frappe.db.get_value("User", {"email": username}, "name", as_dict=True)
        if not user:
            # check by user name
            user = frappe.db.get_value("User", {"username": username}, "name", as_dict=True)
        if not user:
            frappe.throw("Invalid username or password", frappe.AuthenticationError)
        login_manager.authenticate(user, password)
        
        user = frappe.get_doc("User", user)
        tokens = prepare_token(user)
        frappe.db.commit()
        data = frappe._dict()
        data.update({
            "user": user.name,
            "email": user.email,
            "language": user.language,
            "full_name": user.full_name,
        })
        data.update(tokens)
        build_success_response(status_code=200, message="Login successful", data=data)
    except frappe.AuthenticationError as exc:
        build_error_response(status_code=401, message="Invalid username or password", error="Invalid credentials")

@frappe.whitelist(allow_guest=True)
def refresh_token(refresh_token="", user=""):
    user = frappe.db.exists("User", user)
    if not user:
        return build_error_response(status_code=401, message="Invalid or expired refresh token", error="Invalid or expired refresh token")
    now = now_datetime()
    refresh_token_doc = frappe.db.get_value(
        "HR Auth Refresh Token",
        {"refresh_token": refresh_token, "user": user, "status": 'Active', "expiration_time": (">", now)},
        "name"
    )
    if not refresh_token_doc:
        return build_error_response(status_code=401, message="Invalid or expired refresh token", error="Invalid or expired refresh token")
    
    refresh_token_doc = frappe.get_doc("HR Auth Refresh Token", refresh_token_doc)
    user = frappe.get_doc("User", refresh_token_doc.user)
    tokens = prepare_token(user)
    # refresh_token_doc.status = "Revoked"
    # refresh_token_doc.save(ignore_permissions=True)
    frappe.db.commit()
    data = frappe._dict()
    data.update({
        "user": user.name,
        "email": user.email,
        "language": user.language,
        "full_name": user.full_name,
    })
    data.update(tokens)
    build_success_response(status_code=200, message="New access token generated successfully", data=data)

@frappe.whitelist()
def logout():
    if LOGOUT_FROM_ALL:
        frappe.db.sql("""
                UPDATE `tabHR Auth Access Token`
                SET status='Revoked'
                WHERE user=%s
            """, frappe.session.user)
        frappe.db.sql("""
                UPDATE `tabHR Auth Refresh Token`
                SET status='Revoked'
                WHERE user=%s
            """, frappe.session.user)
    else:
        token = get_token_from_header()
        frappe.db.sql("""
                UPDATE `tabHR Auth Access Token`
                SET status='Revoked'
                WHERE access_token=%s
            """, token)
        frappe.db.sql("""
                UPDATE `tabHR Auth Refresh Token`
                SET status='Revoked'
                WHERE access_token=%s
            """, token)
    frappe.db.commit()
    build_success_response(status_code=200, message="Logged out successfully", data=None)

@frappe.whitelist()
def user_info():
    user = frappe.get_doc("User", frappe.session.user)
    employee = get_employee_from_user(frappe.session.user)
    data = frappe._dict()
    data.update({
        "user": user.name,
        "email": user.email,
        "language": user.language,
        "full_name": user.full_name,
        "roles": frappe.get_roles(frappe.session.user)
    })
    data.update(employee)
    build_success_response(status_code=200, message="User Info", data=data)

@frappe.whitelist()
def employee_info(employeeId=""):
    employee = frappe.db.exists("Employee", employeeId)
    if not employee:
        build_error_response(404, "Employee Not found", "The requested employee could not be found")
        return

    employee = frappe.get_doc("Employee", employee)
    if not frappe.has_permission("Employee", "read", employee, frappe.session.user, False):
        build_error_response(403, "Access denied: Insufficient privileges to view this information", "You do not have permission to access employee details")
        return

    data = frappe._dict()
    data.update(employee.as_dict())
    build_success_response(status_code=200, message="Employee {} Details".format(employee.name), data=data)
