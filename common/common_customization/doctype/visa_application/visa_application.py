# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils import nowdate
from common.models.base_hr_document import BaseHRDocument

class VisaApplication(BaseHRDocument):
    def before_validate(self):
        if not self.request_date:
            self.request_date = nowdate()