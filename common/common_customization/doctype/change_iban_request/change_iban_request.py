# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate
from common.models.base_hr_document import BaseHRDocument
from common.utils.validators import validate_iban
class ChangeIBANRequest(BaseHRDocument):
    def before_validate(self):
        if not self.request_date:
            self.request_date = nowdate()
    
    def validate(self):
        super().validate()
        self.validate_iban()
    
    def validate_iban(self):
        if not validate_iban(self.iban):
            frappe.throw(_("Invalid IBAN. Please check the number and try again"))

    def on_submit(self):
        if self.status != 'Approved':
            return
        self.update_employee_bank_details()
    
    def update_employee_bank_details(self):
        employee = frappe.get_doc("Employee", self.employee)
        employee.salary_mode = "Bank"
        employee.bank_name = self.bank_name
        employee.bank_ac_no = self.bank_ac_no
        employee.iban = self.iban
        employee.flags.ignore_permissions = True
        employee.flags.ignore_mandatory = True
        employee.save()
