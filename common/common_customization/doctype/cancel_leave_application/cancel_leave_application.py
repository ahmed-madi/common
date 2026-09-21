# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _, bold
from frappe.utils import nowdate, date_diff, get_link_to_form, cint

from common.models.base_hr_document import BaseHRDocument


class CancelLeaveApplication(BaseHRDocument):
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
            frappe.throw(
                _("Only approved applications can be canceled"),
                frappe.InvalidStatusError,
            )

        if date_diff(leave.from_date, nowdate()) < 1:
            frappe.throw(
                _(
                    "Cancellation is not possible as the application has either already ended or is currently in progress"
                ),
                frappe.InvalidStatusError,
            )

        cancel_allowed_before = cint(
            self.policy_value("cancel_allowed_before")
        )
        if (
            cancel_allowed_before > 0
            and date_diff(leave.from_date, self.request_date) < cancel_allowed_before
        ):
            frappe.throw(
                _(
                    "Cancellation of the application is only allowed if done {} days before the start"
                ).format(cancel_allowed_before),
                frappe.InvalidStatusError,
            )

    def validate_previous_records(self):
        prev = frappe.get_all(
            "Cancel Leave Application",
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
                    "A duplicated cancellation record has been found for the employee: {0}."
                ).format(get_link_to_form("Cancel Leave Application", prev[0].name)),
                frappe.UniqueValidationError,
            )

    def on_submit(self):
        if self.status != "Approved":
            return
        leave = frappe.get_doc("Leave Application", self.leave_application)
        leave.flags.ignore_permissions = True
        leave.cancel()
        leave.add_comment(
            text="Cancelled by employee in {}".format(
                get_link_to_form("Cancel Leave Application", self.name, "Application")
            )
        )
