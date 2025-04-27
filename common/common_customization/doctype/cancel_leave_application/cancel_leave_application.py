# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _, bold
from frappe.utils import nowdate, date_diff
from frappe.model.document import Document


class CancelLeaveApplication(Document):
	def validate(self):
		self.validate_employee()
		self.validate_leave_application()

	def validate_employee(self):
		employee_status = frappe.db.get_value("Employee", self.employee, "status")
		if employee_status != "Active":
			frappe.throw(_("Leave application cancellation is restricted to active employees"))
	
	def validate_leave_application(self):
		leave = frappe.get_doc("Leave Application", self.leave_application)
		if leave.employee != self.employee:
			frappe.throw(_("Leave Application {0} is not Belong to Employee {1}").format(bold(self.leave_application), bold(self.employee)))
		
		if leave.docstatus != 1 or leave.status != "Approved":
			frappe.throw(_("Only approved applications can be canceled"))
		
		if date_diff(leave.from_date, nowdate()) < 1:
			frappe.throw(_("Unable to cancel application currently in progress"))
