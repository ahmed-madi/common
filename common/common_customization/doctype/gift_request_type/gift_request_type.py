# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from erpnext import get_default_company


class GiftRequestType(Document):
    def validate(self):
        self.validate_additional_salary_details()

    def validate_additional_salary_details(self):
        if self.add_to != "Additional Salary":
            return
        if not self.salary_component:
            frappe.throw(_("Salary Component is required for Additional Salary"))

        account = frappe.db.get_value(
            "Salary Component Account",
            {"parent": self.salary_component, "company": get_default_company()},
            "account",
        )
        if not account:
            frappe.throw(
                _("Set account for Salary Component {}").format(self.salary_component)
            )
        if self.total_months <= 0:
            self.total_months = 1
        self.total_cost = cint(self.total_months) * self.gift_cost
