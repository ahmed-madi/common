# Copyright (c) 2024, Mawred and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from cipher.utils import get_employee_from_user
from cipher.utils import EmployeeFetch

class SoftwareLicenseRequest(EmployeeFetch):
    def before_validate(self):
        employee = get_employee_from_user(frappe.session.user)
        if not employee or employee is None:
            return
        manager = frappe.db.get_value("Employee", employee, "reports_to")
        if not manager:
            return
        self.manager = manager
        
    def befor_save(self):

        super().before_insert()
