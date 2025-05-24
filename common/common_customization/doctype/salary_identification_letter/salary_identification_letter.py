# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils import getdate
from common.models.base_hr_document import BaseHRDocument


class SalaryIdentificationLetter(BaseHRDocument):
	def before_validate(self):
		if not self.request_date:
			self.request_date = getdate()

	def on_submit(self):
		if self.status != "Approved":
			return
		self.generate_signed_file()
	
	def generate_signed_file(self):
		pass
