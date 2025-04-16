# Copyright (c) 2024, Mawred and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from cipher.utils import EmployeeFetch


class SecurityMaintenanceSupport(EmployeeFetch):
    
    def befor_save(self):

        super().before_insert()
