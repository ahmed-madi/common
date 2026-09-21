import frappe

from common.employee_snapshot import update_employee


def execute():
    """Fill in the salary and leave figures for employees who already exist.

    The figures are maintained by payslips and leave documents from here on,
    but without this every active employee would show blanks until their next
    payroll run.
    """
    if not frappe.db.table_exists("Salary Slip"):
        return

    for employee in frappe.get_all(
        "Employee", filters={"status": "Active"}, pluck="name"
    ):
        try:
            update_employee(employee)
        except Exception:
            # One employee with, say, no leave allocation must not stop the
            # rest of the backfill.
            frappe.log_error(
                title="Employee snapshot backfill failed",
                message=f"{employee}: {frappe.get_traceback()}",
            )

    frappe.db.commit()
