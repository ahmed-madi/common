# Copyright (c) 2026, Ahmed Madi and contributors
# For license information, please see license.txt

"""Keeping the Employee's salary and leave figures current.

Every document that can change one of them refreshes it on submit and on
cancel. Cancel matters as much as submit: a cancelled payslip or leave
application has to put the figure back, or the Employee keeps a number that no
document supports any more.
"""

import frappe

from common.employee_snapshot import update_employee


def on_salary_slip_change(doc, method=None):
    # The salary comes from the latest submitted payslip, so a cancel has to
    # recompute from whatever is now the latest rather than assume this one.
    refresh(doc, salary=True, leave=False)


def on_leave_change(doc, method=None):
    refresh(doc, salary=False, leave=True)


def refresh(doc, salary, leave):
    """Refresh the Employee, but never at the cost of the document doing it.

    These run inside submit and cancel, so an exception here would roll the
    whole thing back - a leave application refused because a balance could not
    be recalculated. The figure going stale is the lesser failure, and the
    error log says it happened.
    """
    try:
        update_employee(doc.employee, salary=salary, leave=leave)
    except Exception:
        frappe.log_error(
            title="Employee snapshot refresh failed",
            message=f"{doc.doctype} {doc.name} / {doc.employee}: {frappe.get_traceback()}",
        )
