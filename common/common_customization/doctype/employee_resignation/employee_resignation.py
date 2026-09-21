# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, date_diff
from common.models.base_hr_document import BaseHRDocument


class EmployeeResignation(BaseHRDocument):
    def validate(self):
        if hasattr(super(), "validate"):
            super().validate()
        self.validate_notice_days()

    def validate_notice_days(self):
        notice_days = cint(
            self.policy_value("resignation_notice_days")
        )
        if notice_days <= 0:
            return

        if date_diff(self.last_working_day, self.request_date) < notice_days:
            frappe.throw(
                _(
                    "Resignation notice date must be before {} days from Last Working Day"
                ).format(notice_days)
            )
