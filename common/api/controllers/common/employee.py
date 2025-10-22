import frappe
from frappe.utils import getdate, cint

from common.api.utils.response import build_success_response, build_error_response
from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "employee_name", "department", "designation", "date_of_joining"]


def employee_list():
    doctype = "Employee"
    return document_list(doctype, fields, translate_text=True, tr_field="employee_name")


def read_employee(name: str):
    doctype = "Employee"
    return read_doc(doctype, name, origin_fields=fields)


def employee_leave_balance(name: str):
    for_annual: int = frappe.request.values.get("for_annual", 1)
    if not name:
        name = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")

    if not name:
        return build_error_response(
            status_code=400,
            message="Employee ID (name) must be provided",
            error="Employee ID (name) must be provided",
        )

    name = frappe.db.exists("Employee", name)
    if not name:
        return build_error_response(
            404, "Employee Not found", "The requested employee could not be found"
        )
    employee = frappe.get_doc("Employee", name)
    if not frappe.has_permission(
        "Employee", "read", employee, frappe.session.user, False
    ):
        return build_error_response(
            403,
            "Access denied: Insufficient privileges to view this information",
            "You do not have permission to access employee details",
        )

    from hrms.hr.doctype.leave_application.leave_application import get_leave_details

    date = getdate()

    leave_map = {}
    leave_details = get_leave_details(employee.name, date)
    allocation = leave_details["leave_allocation"]

    if cint(for_annual) == 1:
        annual_leave = frappe.db.get_single_value("Company Policy", "annual_leave_type")
        if not annual_leave or annual_leave is None:
            return build_error_response(
                404,
                "Annual Leave not found",
                "Data for Annual Leave Type is not available",
            )
        details = allocation.get(annual_leave, {})
        leave_map[annual_leave] = {
            "leave_type": annual_leave,
            "allocated_leaves": details.get("total_leaves", 0.0),
            "balance_leaves": details.get("remaining_leaves", 0.0),
            "expired_leaves": details.get("expired_leaves", 0.0),
            "leaves_pending_approval": details.get("leaves_pending_approval", 0.0),
        }
        return build_success_response(
            status_code=200,
            message="Employee Annual Leave Balance Details",
            data=leave_map,
        )

    for leave_type, details in allocation.items():
        leave_map[leave_type] = {
            "leave_type": leave_type,
            "allocated_leaves": details.get("total_leaves", 0.0),
            "balance_leaves": details.get("remaining_leaves", 0.0),
            "expired_leaves": details.get("expired_leaves", 0.0),
            "leaves_pending_approval": details.get("leaves_pending_approval", 0.0),
        }
    return build_success_response(
        status_code=200, message="Employee Leave Balance Details", data=leave_map
    )
