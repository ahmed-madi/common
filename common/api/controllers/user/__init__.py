import frappe
from frappe.auth import LoginManager, MAX_PASSWORD_SIZE
from frappe.utils import now_datetime, cint, today
from frappe.core.doctype.user.user import (
    test_password_strength,
    test_password_strength,
    _get_user_for_update_password,
    reset_user_data,
)
from frappe.utils.password import update_password as _update_password

from hrms.hr.doctype.shift_assignment.shift_assignment import get_employee_shift

from common.api.utils.jwt import prepare_token
from common.api.utils.response import build_success_response, build_error_response
from common.api.utils import (
    get_token_from_header,
    get_request_form_data,
    handle_password_test_fail,
)
from common.utils.hr import get_employee_from_user
from common.api.utils.endpoints import document_list

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
        build_success_response(status_code=200, message="Login successful", data=data)
    except frappe.NotFound as exc:
        build_error_response(
            status_code=409,
            message="Invalid employee account",
            error="Invalid credentials",
        )
    except frappe.AuthenticationError as exc:
        build_error_response(
            status_code=401,
            message="Invalid username or password",
            error="Invalid credentials",
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
def user_info():
    user = frappe.get_doc("User", frappe.session.user)
    employee = get_employee_from_user(frappe.session.user)
    data = frappe._dict()
    data.update(
        {
            "user": user.name,
            "email": user.email,
            "language": user.language,
            "full_name": user.full_name,
            "roles": frappe.get_roles(frappe.session.user),
        }
    )
    certifications = achievements = custodies = []
    last_salary_structure_assignment = None
    last_salary_structure = None
    last_salary_slip_based_on_last_salary_structure = None
    last_salary_slip = None
    last_log = None
    employee_shift = None

    if employee and employee.get("name"):
        name = employee.get("name")
        certifications = frappe.db.sql(
            """
                            SELECT name, employee, employee_name, certificate_title, issuing_organization,
                                    date_of_issue, attachment, status, docstatus
                            FROM `tabEmployee Certification`
                            WHERE employee='{}'""".format(
                name
            ),
            as_dict=True,
        )
        achievements = frappe.db.sql(
            """
                            SELECT name, employee, employee_name, title, date, description,
                                    attachment, status, docstatus
                            FROM `tabEmployee Achievement`
                            WHERE employee='{}'""".format(
                name
            ),
            as_dict=True,
        )

        assignments = frappe.get_all(
            "Salary Structure Assignment",
            filters={"employee": name, "docstatus": 1},
            fields=["*"],
            order_by="from_date",
        )
        salary_slip = frappe.get_all(
            "Salary Slip",
            filters={"employee": name, "docstatus": 1},
            fields=["name", "salary_structure"],
            order_by="start_date",
        )
        if len(salary_slip) > 0:
            last_salary_slip = frappe.get_doc("Salary Slip", salary_slip[0].name)

        if len(assignments) > 0:
            last_salary_structure_assignment = assignments[0]
            last_salary_structure = frappe.get_doc(
                "Salary Structure", last_salary_structure_assignment.salary_structure
            )
            for slip in salary_slip:
                if (
                    slip.salary_structure
                    != last_salary_structure_assignment.salary_structure
                ):
                    continue
                last_salary_slip_based_on_last_salary_structure = frappe.get_doc(
                    "Salary Slip", slip.name
                )
                break
        custodies = frappe.db.sql(
            """
                            SELECT *
                            FROM `tabAsset`
                            WHERE docstatus=1 AND custodian='{}'""".format(
                name
            ),
            as_dict=True,
        )
        last_logs = frappe.get_all(
            "Employee Checkin",
            filters={"employee": name},
            fields=[
                "name",
                "employee",
                "employee_name",
                "log_type",
                "time",
                "device_id",
            ],
            order_by="time desc",
        )
        if last_logs:
            last_log = last_logs[0]
        employee_shift = get_employee_shift(
            name, consider_default_shift=True, next_shift_direction="reverse"
        )

    data.update(employee)
    data.update(
        {
            "certifications": certifications,
            "achievements": achievements,
            "last_salary_structure_assignment": last_salary_structure_assignment,
            "last_salary_structure": last_salary_structure,
            "last_salary_slip_based_on_last_salary_structure": last_salary_slip_based_on_last_salary_structure,
            "last_salary_slip": last_salary_slip,
            "custodies": custodies,
            "last_log": last_log,
            "employee_shift": employee_shift,
        }
    )
    build_success_response(status_code=200, message="User Info", data=data)


@frappe.whitelist()
def employee_info(employeeId=""):
    employee = frappe.db.exists("Employee", employeeId)
    if not employee:
        build_error_response(
            404, "Employee Not found", "The requested employee could not be found"
        )
        return

    employee = frappe.get_doc("Employee", employee)
    if not frappe.has_permission(
        "Employee", "read", employee, frappe.session.user, False
    ):
        build_error_response(
            403,
            "Access denied: Insufficient privileges to view this information",
            "You do not have permission to access employee details",
        )
        return
    last_check_in = frappe.get_all("Employee Checkin", filters={"employee": employee.employee}, fields=["log_type", "time"], order_by="time desc")
    if len(last_check_in):
        last_check_in = last_check_in[0]
    else:
        last_check_in = None
    data = frappe._dict()
    data.update(employee.as_dict())
    data.update({
        "checkin_status": last_check_in
    })
    build_success_response(
        status_code=200, message="Employee {} Details".format(employee.name), data=data
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
    except:
        build_error_response(403, "Failed to update password", frappe.get_traceback())


def notification_list():
    doctype = "Notification Log"
    user_filters = {
        "for_user": frappe.session.user,
    }
    fields = [
        "name",
        "subject",
        "for_user",
        "type",
        "email_content",
        "document_type",
        "document_name",
        "read",
        "attached_file",
        "attachment_link",
        "from_user",
        "link",
        "push_notification",
    ]
    return document_list(
        doctype,
        fields,
        force_fields=True,
        force_user_filters=True,
        user_filters=user_filters,
    )


def mark_as_read(docname: str):
    if frappe.flags.read_only:
        return

    if docname:
        frappe.db.set_value(
            "Notification Log", str(docname), "read", 1, update_modified=False
        )
