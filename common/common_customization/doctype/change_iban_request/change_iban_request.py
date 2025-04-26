# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChangeIBANRequest(Document):
	def on_submit(self):
		employee = frappe.get_doc("Employee", self.employee)
		employee.salary_mode = "Bank"
		employee.bank_name = self.bank_name
		employee.bank_ac_no = self.bank_ac_no
		employee.iban = self.iban
