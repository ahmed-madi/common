# Copyright (c) 2024, Mawred and contributors
# For license information, please see license.txt

# import frappe
from common.utils.hr import EmployeeFetch

class SoftwareLicenseRequest(EmployeeFetch):
    def before_validate(self):
        super().before_insert()
