# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document


class HRTicket(Document):
    def validate(self):
        if self.is_new() and flt(self.rating) == 0:
            return
        if self.has_value_changed("rating") and self.docstatus != 1 and self.status != 'Closed':
            frappe.throw(_("Rating allowed for closed tickets only"))
    