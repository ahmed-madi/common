import frappe
from frappe.utils import cint
from frappe.utils import today, get_last_day


def after_insert(doc, method):
    settings = frappe.get_single("HR Settings")

    if not cint(settings.custom_auto_assign_leaves):
        return

    leave_policy = None

    if settings.custom_leave_assign_type == "Leave Policy":
        leave_policy = settings.custom_leave_policy
    elif settings.custom_leave_assign_type == "Custom Assign":
        # Check Custom Assign Criteria
        for d in settings.custom_leave_assign_criteria:
            if d.criteria_type == "Department" and doc.department == d.criteria_value:
                leave_policy = d.leave_policy
                break
            elif (
                d.criteria_type == "Designation" and doc.designation == d.criteria_value
            ):
                leave_policy = d.leave_policy
                break
            elif d.criteria_type == "Employee" and doc.name == d.criteria_value:
                leave_policy = d.leave_policy
                break

        # Fallback to default leave policy if no match found
        if not leave_policy:
            leave_policy = settings.custom_leave_policy

    if not leave_policy:
        frappe.log_error(
            message=f"Leave Policy not assigned for Employee {doc.name}: Policy not found in HR Settings or Criteria",
            title="Leave Policy Assignment Error",
        )
        return

    try:
        # Create Leave Policy Assignment
        assignment = frappe.new_doc("Leave Policy Assignment")
        assignment.employee = doc.name
        assignment.leave_policy = leave_policy
        assignment.assignment_based_on = "Joining Date"
        assignment.effective_from = doc.date_of_joining or today()
        assignment.effective_to = get_last_day(doc.date_of_joining)
        assignment.insert(ignore_permissions=True)
        assignment.submit()
    except Exception:
        frappe.log_error(
            message=frappe.get_traceback(),
            title=f"Leave Policy Assignment failed for {doc.name}",
        )
