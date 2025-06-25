import frappe
from frappe.utils import getdate

from common.api.utils.response import build_success_response, build_error_response
from common.api.utils.endpoints import document_list, read_doc

def employee_list():
    doctype = "Employee"
    fields = ["name", "employee_name", "department", "designation", "date_of_joining"]
    return document_list(doctype, fields)

def read_employee(name: str):
    doctype = "Employee"
    fields = ["name", "employee_name", "department", "designation", "date_of_joining"]
    return read_doc(doctype, name, origin_fields=fields)

def employee_leave_balance(name: str):
    if not name:
        name = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")

    if not name:
        return build_error_response(status_code=400, message="Employee ID (name) must be provided", error="Employee ID (name) must be provided")

    name = frappe.db.exists("Employee", name)
    if not name:
        return build_error_response(404, "Employee Not found", "The requested employee could not be found")
    employee = frappe.get_doc("Employee", name)
    if not frappe.has_permission("Employee", "read", employee, frappe.session.user, False):
        return build_error_response(403, "Access denied: Insufficient privileges to view this information", "You do not have permission to access employee details")

    from hrms.hr.doctype.leave_application.leave_application import get_leave_details
    date = getdate()

    leave_map = {}
    leave_details = get_leave_details(employee.name, date)
    allocation = leave_details["leave_allocation"]

    for leave_type, details in allocation.items():
        leave_map[leave_type] = {
            "leave_type": leave_type,
            "allocated_leaves": details.get("total_leaves", 0.0),
            "balance_leaves": details.get("remaining_leaves", 0.0),
            "expired_leaves": details.get("expired_leaves", 0.0),
            "leaves_pending_approval": details.get("leaves_pending_approval", 0.0),
        }
    return build_success_response(status_code=200, message="Employee Leave Balance Details", data=leave_map)
