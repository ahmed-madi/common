import frappe
from frappe import _
from frappe.email.doctype.email_queue.email_queue import (
    SendMailContext as BaseSendMailContext,
)
from frappe.database.database import savepoint
from email.parser import Parser
from email.policy import SMTP


class SendMailContext(BaseSendMailContext):
    @savepoint(catch=Exception)
    def notify_failed_email(self):
        # Parse the email body to extract the subject
        subject = Parser(policy=SMTP).parsestr(self.queue_doc.message)["Subject"]

        # Construct the notification
        notification = frappe.new_doc("Notification Log")
        notification.for_user = self.queue_doc.owner
        notification.set("type", "Alert")
        notification.from_user = self.queue_doc.owner
        notification.document_type = self.queue_doc.doctype
        notification.document_name = self.queue_doc.name
        notification.subject = _("Failed to send email with subject:") + f" {subject}"
        notification.base_subject = "Failed to send email with subject: {{subject}}"
        notification.base_message = "None"
        notification.base_variables = f'{{"subject": "{subject}"}}'
        try:
            notification.insert()
        except Exception as e:
            frappe.log_error("Failed to create notification log for failed email", e)


def patch_send_mail_context():
    import frappe.email.queue

    frappe.email.queue.SendMailContext = SendMailContext
