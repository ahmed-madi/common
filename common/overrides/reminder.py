import frappe

from frappe.automation.doctype.reminder.reminder import Reminder as BaseReminder


class Reminder(BaseReminder):
    def send_reminder(self):
        if self.notified:
            return

        self.db_set("notified", 1, update_modified=False)

        try:
            notification = frappe.new_doc("Notification Log")
            notification.for_user = self.user
            notification.set("type", "Alert")
            notification.document_type = self.reminder_doctype
            notification.document_name = self.reminder_docname
            notification.subject = self.description
            notification.email_content = None
            notification.base_subject = self.description
            notification.base_message = None
            notification.base_variables = {}
            notification.insert()
        except Exception:
            self.log_error("Failed to send reminder")
