# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import (
    cint,
    flt,
    time_diff_in_hours,
    time_diff_in_seconds,
    get_first_day,
    get_last_day,
    getdate,
)
from hrms.hr.doctype.shift_assignment.shift_assignment import (
    get_employee_shift,
    get_shift_details,
)
from common.utils import get_combine_datetime
from common.models.base_hr_document import BaseHRDocument


class EarlyLeaveApplication(BaseHRDocument):
    def validate(self):
        super().validate()
        self.validate_on_record_in_same_day()
        self.validate_exit_date_time()

    def validate_on_record_in_same_day(self):
        other_requests = frappe.get_all(
            "Early Leave Application",
            filters={
                "employee": self.employee,
                "exit_date": self.exit_date,
                "name": ["!=", self.name],
                "docstatus": ["!=", 2],
            },
        )
        if len(other_requests) > 0:
            frappe.throw(
                _(
                    "You have already submitted an early request in this date {}."
                ).format(self.exit_date)
            )

    def validate_exit_date_time(self):
        policy = self.get_policy()

        exit_datetime = get_combine_datetime(self.exit_date, self.exit_time)
        employee_shift = get_employee_shift(
            self.employee, exit_datetime, True, "forward"
        )
        # If the employee is not assigned to a shift.
        if cint(policy.do_not_permit_early_leave) == 1:
            if not employee_shift or employee_shift is None:
                frappe.throw(
                    _(
                        "Application for early leave is not allowed without an assigned shift"
                    )
                )

        if cint(policy.validate_early_exit) == 0:
            return

        if not employee_shift:
            employee_shift = policy.early_exit_shift_type
            employee_shift = get_shift_details(employee_shift)
        shift_type = employee_shift.get("shift_type", {})
        shift_end_time = shift_type.get("end_time", {})

        if not shift_end_time:
            return

        shift_end_time = get_combine_datetime(self.exit_date, shift_end_time)
        if time_diff_in_seconds(exit_datetime, shift_end_time) > 0:
            frappe.throw(_("The exit time is outside of the scheduled shift hours"))

        total_exit_hours = time_diff_in_hours(shift_end_time, exit_datetime)
        self.total_exit_hours = flt(total_exit_hours, 2)
        if flt(policy.early_exit_max_hours_per_day) > 0 and total_exit_hours > flt(
            policy.early_exit_max_hours_per_day
        ):
            frappe.throw(
                _(
                    "You have exceeded the allowed exit hours for today. {} hours Allowed, {} requested"
                ).format(
                    flt(policy.early_exit_max_hours_per_day, 2),
                    flt(total_exit_hours, 2),
                )
            )

        start_month = get_first_day(self.exit_date)
        end_month = get_last_day(self.exit_date)

        total_current_month = frappe.db.sql(
            """
                            SELECT SUM(total_exit_hours) as total
                            FROM `tabEarly Leave Application` 
                            WHERE employee='{}' AND docstatus=1 AND status='Approved'
                            AND exit_date BETWEEN '{}' AND '{}'
                            """.format(
                self.employee, getdate(start_month), getdate(end_month)
            )
        )
        total_in_month = flt(total_exit_hours, 2)
        if total_current_month:
            total_in_month += flt(total_current_month[0][0])
        if flt(policy.early_exit_total_hours_allowed) > 0 and total_in_month > flt(
            policy.early_exit_total_hours_allowed
        ):
            frappe.throw(
                _(
                    "You have exceeded the allowed exit hours for this month. {} hours Allowed, {} requested"
                ).format(
                    flt(policy.early_exit_total_hours_allowed, 2),
                    flt(total_in_month, 2),
                )
            )

    def on_submit(self):
        if self.status != "Approved":
            return
        self.mark_attendance_log_in_exit_date()

    def mark_attendance_log_in_exit_date(self):
        exit_datetime = get_combine_datetime(self.exit_date, self.exit_time)
        employee_shift = get_employee_shift(
            self.employee, exit_datetime, True, "forward"
        )
        shift_type = employee_shift.get("shift_type", {})
        shift_end_time = shift_type.get("end_time", {})
        if not shift_end_time:
            return
        shift_end_time = get_combine_datetime(self.exit_date, shift_end_time)
        doc = frappe.new_doc("Employee Checkin")
        doc.employee = self.employee
        doc.time = shift_end_time
        doc.log_type = "OUT"
        doc.insert()
