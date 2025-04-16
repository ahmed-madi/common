import frappe
from frappe.model.document import Document

class EmployeeFetch(Document):
    def before_insert(self):
        if hasattr(self, "employee"):
            if not self.employee:
                self.employee = frappe.get_value("Employee", dict(user_id=self.owner), "name")
