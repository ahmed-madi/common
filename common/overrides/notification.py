import re
import json

import frappe
from frappe.utils import cint, get_site_path
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
)

from frappe.email.doctype.notification.notification import (
    Notification,
    get_reference_doctype,
    get_reference_name,
)
from frappe.desk.doctype.notification_log.notification_log import NotificationLog

import firebase_admin
from firebase_admin import credentials, messaging


class CustomNotification(Notification):
    def create_system_notification(self, doc, context):
        subject = self.subject
        if "{" in subject:
            subject = frappe.render_template(self.subject, context)

        attachments = self.get_attachment(doc)

        recipients, cc, bcc = self.get_list_of_recipients(doc, context)

        users = recipients + cc + bcc

        if not users:
            return

        notification_doc = {
            "type": "Alert",
            "document_type": get_reference_doctype(doc),
            "document_name": get_reference_name(doc),
            "subject": subject,
            "from_user": doc.modified_by or doc.owner,
            "email_content": frappe.render_template(self.message, context),
            "attached_file": attachments and json.dumps(attachments[0]),
            "push_notification": cint(self.send_push_notification),
        }
        enqueue_create_notification(users, notification_doc)


class CustomNotificationLog(NotificationLog):
    def after_insert(self):
        super().after_insert()
        file_path = frappe.db.get_single_value("FCM Settings", "service_account_file")
        if (
            cint(self.push_notification) == 1
            and cint(frappe.db.get_single_value("FCM Settings", "enable")) == 1
            and file_path
            and self.allow_to_send_push_notification()
        ):
            self.send_push_notification(file_path)

    def allow_to_send_push_notification(self):
        if not self.document_type or self.document_type is None:
            return False

        exists = frappe.db.exists(
            "HR Notification Settings", {"user": frappe.session.user}
        )
        if not exists or exists is None:
            return False
        doc = frappe.get_doc("HR Notification Settings", exists)
        if doc.task_assignments == 1:
            task_documents = frappe.get_all(
                "FRM DocType",
                {"parent": "FCM Settings", "parentfield": "task_documents"},
                pluck="document",
            )
            if self.document_type in task_documents:
                return True
        if doc.request_approvals == 1:
            hr_requests = frappe.get_all(
                "FRM DocType",
                {"parent": "FCM Settings", "parentfield": "hr_requests"},
                pluck="document",
            )
            if self.document_type in hr_requests:
                return True
        if doc.calendar_events == 1:
            event_documents = frappe.get_all(
                "FRM DocType",
                {"parent": "FCM Settings", "parentfield": "event_documents"},
                pluck="document",
            )
            if self.document_type in event_documents:
                return True
        if doc.helpdesk_updates == 1:
            helpdesk_documents = frappe.get_all(
                "FRM DocType",
                {"parent": "FCM Settings", "parentfield": "helpdesk_documents"},
                pluck="document",
            )
            if self.document_type in helpdesk_documents:
                return True
        if doc.performance_reviews == 1:
            performance_documents = frappe.get_all(
                "FRM DocType",
                {"parent": "FCM Settings", "parentfield": "helpdesk_documents"},
                pluck="document",
            )
            if self.document_type in performance_documents:
                return True
        return False

    def send_push_notification(self, file_path):
        cred_path = f"{get_site_path()}{file_path}"
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            self.send_fcm_notification()
        except FileNotFoundError:
            frappe.log_error(
                title="Invalid Credentials file",
                message=f"Error: Credentials file not found at '{file_path}'. Please ensure the path is correct.",
            )
            return
        except ValueError as e:
            if str(e).startswith("The default Firebase app already exists"):
                pass  # App already initialized
            else:
                frappe.log_error(
                    title="Error initializing Firebase app", message=f"{e}"
                )
                return
        except Exception as e:
            frappe.log_error(
                title="An unexpected error occurred during Firebase app initialization",
                message=f"{e}",
            )
            return

    def get_valid_fcm_message(self, txt):
        CLEANER = re.compile("<.*?>")
        clean_message = re.sub(CLEANER, "", txt)
        return clean_message

    def send_fcm_notification(self):
        errors_tokens = []
        for token in frappe.get_all(
            "FCM Device Token", filters={"user": self.for_user}, fields=["token"]
        ):
            message = messaging.Message(
                notification=messaging.Notification(
                    title=self.get_valid_fcm_message(self.subject),
                    body=self.get_valid_fcm_message(self.email_content),
                ),
                data={
                    "document_type": self.document_type or "",
                    "document_name": self.document_name or "",
                    "type": self.type or "",
                    "read": self.read or "",
                    "attached_file": self.attached_file or "",
                    "attachment_link": self.attachment_link or "",
                    "link": self.link or "",
                },
                token=token.token,
            )

            try:
                response = messaging.send(message)
            except messaging.FirebaseError as e:
                firebase_error = f"Error code: {e.code}\nError details: {e.message}"
                frappe.log_error(
                    title="Firebase Messaging Error (single device)",
                    message=f"{e}\n\n{firebase_error}",
                )
            except Exception as e:
                frappe.log_error(
                    title="An unexpected error occurred while sending the message (single device)",
                    message=f"{e}",
                )
            finally:
                for ft in errors_tokens:
                    pass
