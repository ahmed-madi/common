# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _, bold
from frappe.utils import (
    add_days,
    date_diff,
    nowdate,
    format_date,
    get_url_to_list,
    get_link_to_form,
    cint,
)
from hrms.hr.utils import get_leave_period
from common.models.base_hr_document import BaseHRDocument


class LeaveSuspension(BaseHRDocument):
    def validate(self):
        super().validate()
        self.validate_leave_application()
        self.validate_previous_records()

    def validate_leave_application(self):
        leave = frappe.get_doc("Leave Application", self.leave_application)
        if leave.employee != self.employee:
            frappe.throw(
                _("Leave Application {0} is not Belong to Employee {1}").format(
                    bold(self.leave_application), bold(self.employee)
                )
            )

        if leave.docstatus != 1 or leave.status != "Approved":
            frappe.throw(_("Only approved applications can be suspense"))

        if date_diff(leave.from_date, nowdate()) > 0:
            frappe.throw(_("Unable to suspense future application"))

        if date_diff(leave.from_date, self.return_date) > 0:
            frappe.throw(_("Return to work date must be after leave start date"))

        if date_diff(self.return_date, leave.to_date) > 0:
            frappe.throw(_("Return to work date must be before end of leave"))

    def validate_previous_records(self):
        prev = frappe.get_all(
            "Leave Suspension",
            filters={
                "leave_application": self.leave_application,
                "employee": self.employee,
                "docstatus": ["!=", 2],
                "name": ["!=", self.name],
            },
        )
        if len(prev) > 0:
            frappe.throw(
                _(
                    "A duplicated suspension record has been found for the employee: {0}."
                ).format(get_link_to_form("Leave Suspension", prev[0].name)),
                frappe.UniqueValidationError,
            )

    def on_submit(self):
        if self.status != "Approved":
            return
        return_unused_days = (
            frappe.db.get_single_value("Company Policy", "return_unused_days")
            or "Return to Balance"
        )
        if return_unused_days == "Return to Balance":
            self.return_leave_balance()
        elif return_unused_days == "Return as Encashment":
            self.make_leave_encashment()

    def return_leave_balance(self):
        leave = frappe.get_doc("Leave Application", self.leave_application)
        self.create_leave_ledger_entry(leave)
        self.cancel_attendance(leave)

    def create_leave_ledger_entry(self, leave, submit=True):
        company = frappe.db.get_value("Employee", self.employee, "company")
        date_difference = (date_diff(leave.to_date, self.return_date) + 1) * (
            1 if submit else -1
        )
        comp_leave_valid_from = add_days(leave.to_date, 1)
        leave_period = get_leave_period(
            comp_leave_valid_from, comp_leave_valid_from, company
        )
        if leave_period:
            leave_allocation = self.get_existing_allocation(
                comp_leave_valid_from, leave
            )
            if leave_allocation:
                leave_allocation.new_leaves_allocated += date_difference
                leave_allocation.save()
            else:
                leave_allocation = self.create_leave_allocation(
                    leave_period, date_difference
                )
        else:
            comp_leave_valid_from = frappe.bold(format_date(comp_leave_valid_from))
            msg = _("This suspension leave will be applicable from {0}.").format(
                comp_leave_valid_from
            )
            msg += " " + _(
                "Currently, there is no {0} leave period for this date to create/update leave allocation."
            ).format(frappe.bold(_("active")))
            msg += "<br><br>" + _(
                "Please create a new {0} for the date {1} first."
            ).format(
                f"""<a href='{get_url_to_list("Leave Period")}'>Leave Period</a>""",
                comp_leave_valid_from,
            )
            frappe.throw(msg, title=_("No Leave Period Found"))
        leave.add_comment(
            text="Suspension Leave by employee in {} for {} Day(s)".format(
                get_link_to_form("Leave Suspension", self.name, "Application"),
                date_difference,
            )
        )

    def get_existing_allocation(self, comp_leave_valid_from, leave) -> dict | None:
        leave_allocation = frappe.db.get_all(
            "Leave Allocation",
            filters={
                "employee": self.employee,
                "leave_type": leave.leave_type,
                "from_date": ("<=", comp_leave_valid_from),
                "to_date": (">=", comp_leave_valid_from),
                "docstatus": 1,
            },
            limit=1,
        )

        if leave_allocation:
            return frappe.get_doc("Leave Allocation", leave_allocation[0].name)

    def create_leave_allocation(self, leave_period, date_difference):
        is_carry_forward = frappe.db.get_value(
            "Leave Type", self.leave_type, "is_carry_forward"
        )
        allocation = frappe.get_doc(
            dict(
                doctype="Leave Allocation",
                employee=self.employee,
                employee_name=self.employee_name,
                leave_type=self.leave_type,
                from_date=add_days(self.work_end_date, 1),
                to_date=leave_period[0].to_date,
                carry_forward=cint(is_carry_forward),
                new_leaves_allocated=date_difference,
                total_leaves_allocated=date_difference,
                description=self.reason,
            )
        )
        allocation.flags.ignore_permissions = True
        allocation.insert()
        allocation.submit()
        return allocation

    def cancel_attendance(self, leave):
        if self.docstatus == 1:
            attendance = frappe.db.sql(
                """select name from `tabAttendance` where employee = %s\
				and (attendance_date between %s and %s) and docstatus < 2 and status in ('On Leave', 'Half Day')""",
                (self.employee, self.return_date, leave.to_date),
                as_dict=1,
            )
            for name in attendance:
                frappe.db.set_value("Attendance", name, "docstatus", 2)

    def make_leave_encashment(self):
        pass

    def on_cancel(self):
        if hasattr(super(), "on_cancel"):
            super().on_cancel()
        leave = frappe.get_doc("Leave Application", self.leave_application)
        self.create_leave_ledger_entry(leave, False)
