# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class DepartmentContact(Document):
    def validate(self):
        self.validate_reply_to()

    def validate_reply_to(self):
        if not self.is_reply:
            return
        if not self.reply_to:
            frappe.throw(_("Please select a replay to"))
        if self.name == self.reply_to:
            frappe.throw(_("You can't replay to this same contact"))
        replay = frappe.get_doc("Department Contact", self.reply_to)
        if replay.from_employee != self.from_employee:
            frappe.throw(_("You can't replay to this contact"))
        if replay.department != self.department:
            frappe.throw(_("You can't replay to this contact"))
