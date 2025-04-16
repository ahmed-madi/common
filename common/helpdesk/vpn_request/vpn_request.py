# Copyright (c) 2024, Mawred and contributors
# For license information, please see license.txt

import frappe
from cipher.utils import EmployeeFetch


class VPNRequest(EmployeeFetch):

    def befor_validate(self):

        super().before_insert()
