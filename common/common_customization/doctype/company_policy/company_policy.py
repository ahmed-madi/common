# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document


class CompanyPolicy(Document):
    def validate(self):
        pass

    def validate_education_allowance_policy(self):
        # Expense Claim Type
        account = frappe.db.get_value(
            "Expense Claim Account",
            {"parent": self.expense_claim_type, "company": self.company},
            "default_account",
        )
        if not account:
            frappe.throw(
                _("Set the default account for the {0} {1}").format(
                    frappe.bold(_("Expense Claim Type")),
                    get_link_to_form("Expense Claim Type", self.expense_claim_type),
                )
            )
