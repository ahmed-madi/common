# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from common.models.base_hr_document import BaseHRDocument

class DocumentRequest(BaseHRDocument):
	def before_validate(self):
		if not self.request_date:
			self.request_date = getdate()
	
	def validate(self):
		super().validate()
		self.validate_document_file()
	
	def validate_document_file(self):
		if self.docstatus != 1:
			return
		if self.status != "Approved":
			return
		if not self.ready_document or self.ready_document is None:
			frappe.throw(_("Upload requested document before Approved request"))

