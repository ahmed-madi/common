import frappe
from frappe.utils import cint
from hrms.hr.doctype.leave_type.leave_type import LeaveType as BaseLeaveType


class LeaveType(BaseLeaveType):
    def on_update(self):
        if hasattr(super(), "on_update"):
            super().on_update()
        self.update_attachment_required_in_leave_application()
        self.update_reason_required_in_leave_application()

    def update_attachment_required_in_leave_application(self):
        if self.has_value_changed("attachment_required"):
            LeaveApplication = frappe.qb.DocType("Leave Application")
            (
                frappe.qb.update(LeaveApplication)
                .set("attachment_required", cint(self.attachment_required))
                .where(
                    (LeaveApplication.docstatus == 0)
                    & (LeaveApplication.leave_type == self.name)
                )
            ).run()
            frappe.db.commit()

    def update_reason_required_in_leave_application(self):
        if self.has_value_changed("reason_required"):
            LeaveApplication = frappe.qb.DocType("Leave Application")
            (
                frappe.qb.update(LeaveApplication)
                .set("reason_required", cint(self.reason_required))
                .where(
                    (LeaveApplication.docstatus == 0)
                    & (LeaveApplication.leave_type == self.name)
                )
            ).run()
            frappe.db.commit()
