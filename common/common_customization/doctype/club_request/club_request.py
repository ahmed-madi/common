# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cint
from common.models.base_hr_document import BaseHRDocument


class ClubRequest(BaseHRDocument):
    def before_validate(self):
        if int(self.is_paid) == 0:
            self.participation_price = 0

    def validate(self):
        super().validate()
        self.validate_is_paid()
        self.validate_from_to_dates(
            self.start_date, self.end_date, "End date can not be before start date"
        )

    def validate_is_paid(self):
        if cint(self.is_paid) == 1 and flt(self.participation_price) <= 0:
            frappe.throw(
                _("Training price must be greater that zero for paid training")
            )
