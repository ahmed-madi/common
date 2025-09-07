import frappe
from frappe.model.document import Document


class EmployeeFetch(Document):
    def before_insert(self):
        if hasattr(self, "employee"):
            if not self.employee:
                self.employee = frappe.get_value(
                    "Employee", dict(user_id=self.owner), "name"
                )


def get_employee_from_user(user):
    employee_docname = frappe.db.get_value("Employee", {"user_id": user})
    if employee_docname:
        return frappe.get_doc("Employee", employee_docname).as_dict()
    return {}
