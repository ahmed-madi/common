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
from firebase_admin.exceptions import FirebaseError

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
            "FCM Device Token", filters={"user": self.for_user}, fields=["name", "token"]
        ):
            subject = self.subject
            if not isinstance(subject, str):
                subject = "{}".format(subject).strip()
            
            for_user = self.for_user
            if not isinstance(for_user, str):
                for_user = "{}".format(for_user).strip()
            
            type = self.type
            if not isinstance(type, str):
                type = "{}".format(type).strip()

            email_content = self.email_content
            if not isinstance(email_content, str):
                email_content = "{}".format(email_content).strip()
            
            document_type = self.document_type
            if not isinstance(document_type, str):
                document_type = "{}".format(document_type).strip()
            
            read = self.read
            if not isinstance(read, str):
                read = "{}".format(read).strip()
            
            document_name = self.document_name
            if not isinstance(document_name, str):
                document_name = "{}".format(document_name).strip()
            
            attached_file = self.attached_file
            if not isinstance(attached_file, str):
                attached_file = "{}".format(attached_file).strip()
            
            from_user = self.from_user
            if not isinstance(from_user, str):
                from_user = "{}".format(from_user).strip()
            
            link = self.link
            if not isinstance(link, str):
                link = "{}".format(link)
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=self.get_valid_fcm_message(subject),
                    body=self.get_valid_fcm_message(email_content),
                ),
                data={
                    "subject": subject or "",
                    "for_user": for_user,
                    "type": type or "",
                    "email_content": email_content or "",
                    "document_type": document_type or "",
                    "read": read or "0",
                    "document_name": document_name or "",
                    "attached_file": attached_file or "",
                    # "attachment_link": self.attachment_link or "",
                    "from_user": from_user or "",
                    "link": link or "",
                },
                token=token.token,
            )

            try:
                messaging.send(message)
            except FirebaseError as e:
                firebase_error = f"Error code: {e.code}\nError details: {e}"
                frappe.log_error(
                    title="Firebase Messaging Error (single device)",
                    message=f"{e}\n\n{firebase_error}",
                )
                if e.code in ["UNREGISTERED"]:
                    frappe.delete_doc_if_exists(token.name, force=True)
            except Exception as e:
                frappe.log_error(
                    title="An unexpected error occurred while sending the message (single device)",
                    message=f"{e}\n{frappe.get_traceback()}",
                )
            finally:
                for ft in errors_tokens:
                    pass
