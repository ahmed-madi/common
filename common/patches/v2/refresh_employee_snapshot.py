import frappe

from common.employee_snapshot import update_employee


def execute():
    """Recompute the salary and annual leave figures every active employee carries.

    They are only refreshed when a payslip, leave application or leave
    allocation is submitted or cancelled. Anything that changed them without
    one - earned leave accrual, a reclassified salary component, an employee
    moved to another company - left them stale.
    """
    if not frappe.db.table_exists("Salary Slip"):
        return

    for employee in frappe.get_all(
        "Employee", filters={"status": "Active"}, pluck="name"
    ):
        try:
            update_employee(employee)
        except Exception:
            # One employee with a broken setup must not stop the rest.
            frappe.log_error(
                title="Employee snapshot refresh failed",
                message=f"{employee}: {frappe.get_traceback()}",
            )

    frappe.db.commit()
