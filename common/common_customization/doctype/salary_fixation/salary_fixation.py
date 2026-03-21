# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from common.models.base_hr_document import BaseHRDocument


class SalaryFixation(BaseHRDocument):
    def validate(self):
        super().validate()
        self.validate_backdate_restriction(
            "restrict_backdated_sfx", "sfx_w_roles", self.effective_date
        )
        self.validate_salary_mode()

    def validate_salary_mode(self):
        salary_mode_details = frappe.db.get_values(
            "Employee", self.employee, ["salary_mode", "iban"], as_dict=True
        )
        if not salary_mode_details:
            frappe.throw(
                _("Salary mode for {} must be 'Bank'").format(
                    get_link_to_form("Employee", self.employee, _("Employee"))
                )
            )
        salary_mode = salary_mode_details[0].get("salary_mode")

        if salary_mode != "Bank":
            frappe.throw(
                _("Salary mode for {} must be 'Bank'").format(
                    get_link_to_form("Employee", self.employee, _("Employee"))
                )
            )

        iban = salary_mode_details[0].get("iban")
        if not iban:
            frappe.throw(
                _("Selected Employee {} must have a valid IBAN").format(
                    get_link_to_form("Employee", self.employee, _("Employee"))
                )
            )
