import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
    get_title,
    get_title_html,
)
from frappe.utils import get_fullname


def notify_mentions(ref_doctype, ref_name, content):
    if ref_doctype and ref_name and content:
        mentions = frappe.desk.notifications.extract_mentions(content)
        if not mentions:
            return

        sender_fullname = get_fullname(frappe.session.user)
        title = get_title(ref_doctype, ref_name)

        recipients = [
            frappe.db.get_value(
                "User",
                {
                    "enabled": 1,
                    "name": name,
                    "user_type": "System User",
                    "allowed_in_mentions": 1,
                },
                "email",
            )
            for name in mentions
        ]

        notification_message = _(
            """{0} mentioned you in a comment in {1} {2}"""
        ).format(
            frappe.bold(sender_fullname),
            frappe.bold(ref_doctype),
            get_title_html(title),
        )

        notification_doc = {
            "type": "Mention",
            "document_type": ref_doctype,
            "document_name": ref_name,
            "subject": notification_message,
            "base_subject": "{{sender_fullname}} mentioned you in a comment in {{_(doctype)}} {{doc_name}}",
            "base_message": "Mention in {{doctype}} {{doc_name}}",
            "base_variables": f'{{"sender_fullname": "{sender_fullname}", "doctype": "{ref_doctype}", "doc_name": "{ref_name}"}}',
            "from_user": frappe.session.user,
            "email_content": content,
        }
        enqueue_create_notification(recipients, notification_doc)


def patch_notify_mentions():
    import frappe.desk.notifications

    frappe.desk.notifications.notify_mentions = notify_mentions
