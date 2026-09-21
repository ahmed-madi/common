# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cint, date_diff
from common.models.base_hr_document import BaseHRDocument


class TrainingRequest(BaseHRDocument):
    def validate(self):
        super().validate()
        self.validate_from_to_dates(
            self.start_date, self.end_date, "End date cannot be before start date"
        )
        self.validate_training_price()
        self.validate_training_duration()
        self.validate_training_policy()

    def validate_training_price(self):
        if flt(self.training_price) >= 0:
            return
        frappe.throw(_("Training price must be negative"))

    def validate_training_duration(self):
        if flt(self.training_duration) > 0:
            return
        frappe.throw(_("Training price must be greater than zero"))

    def validate_training_policy(self):
        training_allowed_before = cint(
            self.policy_value("training_allowed_before")
        )
        if (
            training_allowed_before > 0
            and date_diff(self.start_date, self.request_date) < training_allowed_before
        ):
            frappe.throw(
                _("Training request must be before {} days from start").format(
                    training_allowed_before
                ),
                frappe.InvalidStatusError,
            )
