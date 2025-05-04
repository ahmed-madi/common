import frappe
from frappe import _
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication as BaseLeaveApplication

class LeaveApplication(BaseLeaveApplication):
    def before_validate(self):
        if hasattr(super(), 'before_validate'):
            super().before_validate()
        self.make_reason_clean()
    
    def make_reason_clean(self):
        if not isinstance(self.description, str):
            return
        description = self.description.strip()
        self.description = description

    def validate(self):
        if hasattr(super(), 'validate'):
            super().validate()
        self.validate_attachment()
        self.validate_reason()
    
    def validate_attachment(self):
        if frappe.db.get_value("Leave Type", self.leave_type, "attachment_required") == 1 and not self.attachment:
            frappe.throw(_("Attachment for Leave Type {0} is Required").format(_(self.leave_type)), frappe.MandatoryError)

    def validate_reason(self):
        if frappe.db.get_value("Leave Type", self.leave_type, "reason_required") == 1 and not self.description or len(self.description) == 0:
            frappe.throw(_("Reason for Leave Type {0} is Required").format(_(self.leave_type)), frappe.MandatoryError)
