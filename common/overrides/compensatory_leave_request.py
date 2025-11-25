import frappe
from frappe import _
from frappe.utils import getdate, format_date, date_diff
from hrms.hr.doctype.compensatory_leave_request.compensatory_leave_request import (
    CompensatoryLeaveRequest as BaseCompensatoryLeaveRequest,
)


class CompensatoryLeaveRequest(BaseCompensatoryLeaveRequest):
    def validate_attendance(self):
        attendance_records = frappe.get_all(
            "Attendance",
            filters={
                "attendance_date": [
                    "between",
                    (self.work_from_date, self.work_end_date),
                ],
                "status": (
                    "in",
                    ["Present", "Work From Home", "Half Day", "Work Outside Office"],
                ),
                "half_day_status": ("!=", "Absent"),
                "docstatus": 1,
                "employee": self.employee,
            },
            fields=["attendance_date", "status"],
        )

        half_days = [
            entry.attendance_date
            for entry in attendance_records
            if entry.status == "Half Day"
        ]

        if half_days and (
            not self.half_day or getdate(self.half_day_date) not in half_days
        ):
            frappe.throw(
                _(
                    "You were only present for Half Day on {}. Cannot apply for a full day compensatory leave"
                ).format(
                    ", ".join(
                        [frappe.bold(format_date(half_day)) for half_day in half_days]
                    )
                )
            )

        # if (
        #     len(attendance_records)
        #     < date_diff(self.work_end_date, self.work_from_date) + 1
        # ):
        #     frappe.throw(
        #         _(
        #             "You are not present all day(s) between compensatory leave request days"
        #         )
        #     )

    def on_submit(self):
        if self.status in ["Open", "Cancelled"]:
            frappe.throw(
                _(
                    "Only Applications with status 'Approved' and 'Rejected' can be submitted"
                )
            )
        if self.status != "Approved":
            return
        if hasattr(super(), "on_submit"):
            super().on_submit()

    def before_cancel(self):
        if hasattr(super(), "before_cancel"):
            super().before_cancel()
        self.status = "Cancelled"
