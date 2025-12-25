import frappe
from frappe import _
from frappe.utils import time_diff_in_seconds, now, quote, cint
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
)
from frappe.core.doctype.submission_queue.submission_queue import (
    SubmissionQueue as BaseSubmissionQueue,
)


class SubmissionQueue(BaseSubmissionQueue):
    def notify(self, submission_status: str, action: str):
        if submission_status == "Failed":
            doctype = self.doctype
            docname = self.name
            message = _("Action {0} failed on {1} {2}. View it {3}")
            base_subject = "Action {{action}} failed on {{_(doctype)}} {{docname}}"
            base_variables = f'{{"action": "{action}", "doctype": "{doctype}", "docname": "{docname}"}}'
        else:
            doctype = self.ref_doctype
            docname = self.ref_docname
            message = _("Action {0} completed successfully on {1} {2}. View it {3}")
            base_subject = (
                "Action {{action}} completed successfully on {{_(doctype)}} {{docname}}"
            )
            base_variables = f'{{"action": "{action}", "doctype": "{doctype}", "docname": "{docname}"}}'

        message_replacements = (
            frappe.bold(action),
            frappe.bold(str(self.ref_doctype)),
            frappe.bold(str(self.ref_docname)),
        )

        time_diff = time_diff_in_seconds(now(), self.created_at)
        if cint(time_diff) <= 60:
            frappe.publish_realtime(
                "msgprint",
                {
                    "message": message.format(
                        *message_replacements,
                        f"<a href='/app/{quote(doctype.lower().replace(' ', '-'))}/{quote(docname)}'><b>here</b></a>",
                    ),
                    "alert": True,
                    "indicator": "red" if submission_status == "Failed" else "green",
                },
                user=self.enqueued_by,
            )
        else:
            notification_doc = {
                "type": "Alert",
                "document_type": doctype,
                "document_name": docname,
                "subject": message.format(*message_replacements, "here"),
                "base_subject": base_subject,
                "base_variables": base_variables,
            }

            notify_to = frappe.db.get_value("User", self.enqueued_by, fieldname="email")
            enqueue_create_notification([notify_to], notification_doc)
