# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, flt, get_link_to_form

from erpnext import get_default_cost_center

from common.models.base_hr_document import BaseHRDocument

class EducationAllowanceRequest(BaseHRDocument):
    def before_validate(self):
        if not self.request_date:
            self.request_date = nowdate()
    
    def validate(self):
        self.check_expense_type()
        super().validate()
        self.validate_requested_amount()
        self.validate_for_children()
    
    def validate_for_children(self):
        pass
    
    def check_expense_type(self):
        if not frappe.db.get_single_value("Company Policy", "expense_claim_type"):
            frappe.throw(
                _("Expense Claim Type is not added in {0}").format(
                    get_link_to_form("Company Policy", "Company Policy", _("Company Policy")),
                )
            )

    def validate_requested_amount(self):
        if flt(self.amount_requested) <= 0:
            frappe.throw(_("Requested amount can not be zero or negative number"))
        max_education_allowance = flt(frappe.db.get_single_value("Company Policy", "max_education_allowance"))
        if max_education_allowance > 0 and flt(self.amount_requested) > max_education_allowance:
            frappe.throw(
                _("You have exceeded the maximum allowed education allowance, {}").format(
                    max_education_allowance,
                )
            )

    def on_submit(self):
        if self.status != 'Approved':
            return
        self.create_expense_claim()
    
    def create_expense_claim(self):
        expense_type = frappe.db.get_single_value("Company Policy", "expense_claim_type")
        payable_account = frappe.db.get_single_value("Company Policy", "expense_claim_account")
        company = frappe.db.get_single_value("Company Policy", "company")
        expense_claim  = frappe.new_doc("Expense Claim")
        expense_claim.employee = self.employee
        expense_claim.payable_account = payable_account
        expense_claim.approval_status = 'Approved'
        expense_claim.append("expenses", {
            "expense_type": expense_type,
            "amount": flt(self.amount_requested),
            "sanctioned_amount": flt(self.amount_requested),
            "cost_center": get_default_cost_center(company)
        })
        expense_claim.flags.ignore_permissions = True
        expense_claim.save()
        expense_claim.submit()
        self.db_set("linked_expense_claim", expense_claim.name)
        # make payment against expense claim
        self.make_payment_entry(expense_claim)  

    def make_payment_entry(self, expense_claim):
        from hrms.overrides.employee_payment_entry import get_payment_entry_for_employee
        payment_entry = get_payment_entry_for_employee(expense_claim.doctype, expense_claim.name)
        payment_entry.flags.ignore_permissions = True
        payment_entry.reference_no = self.name
        payment_entry.reference_date = self.request_date
        payment_entry.flags.ignore_permissions = True
        payment_entry.save()
        payment_entry.submit()

    def on_cancel(self):
        if not self.linked_expense_claim:
            return
        expense_claim  = frappe.get_doc("Expense Claim", self.linked_expense_claim)
        if expense_claim.docstatus != 1:
            return
        expense_claim.flags.ignore_permissions = True
        expense_claim.cancel()
