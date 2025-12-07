from frappe import _
import frappe
from common.api.utils.resource import BaseResource
from common.api.utils.endpoints import document_list
from common.api.utils.decorators import safe_api
from werkzeug.routing import Rule

class NotificationResource(BaseResource):
    doctype = "Notification Log"
    url_prefix = "/user"
    resource_name = "notifications"
    fields = [
        "name",
        "subject",
        "for_user",
        "type",
        "email_content",
        "document_type",
        "document_name",
        "read",
        "attached_file",
        "attachment_link",
        "from_user",
        "link",
        "push_notification",
    ]

    @classmethod
    def list(cls):
        @safe_api
        def _list():
            user_filters = []
            if frappe.session.user != "Administrator":
                user_filters.append(["for_user", "=", frappe.session.user])
            return document_list(
                cls.doctype,
                cls.fields,
                force_user_filters=True,
                user_filters=user_filters,
                add_perms=False,
                add_wf=False,
            )
        _list.__name__ = "notification_list"
        return _list

    @classmethod
    def mark_as_read(cls):
        @safe_api
        def _action(docname):
            if frappe.flags.read_only:
                return
            if docname:
                frappe.db.set_value(
                    "Notification Log", str(docname), "read", 1, update_modified=False
                )
            return {}, _("Marked as read")
        _action.__name__ = "mark_as_read"
        return _action

    @classmethod
    def mark_all_as_read(cls):
        @safe_api
        def _action():
            # Original code called frappe.desk...mark_all_as_read
            # handle_call("frappe.desk.doctype.notification_log.notification_log.mark_all_as_read")
            # We can can call it directly or replicate logic.
            # Calling module method directly is safer if available.
            from frappe.desk.doctype.notification_log.notification_log import mark_all_as_read
            mark_all_as_read()
            return {}, _("All Notification marked as Read")
        _action.__name__ = "mark_all_notifications_as_read"
        return _action

    @classmethod
    def get_routes(cls):
        return [
            Rule("/user/notifications", methods=["GET"], endpoint=cls.list()),
            Rule(
                "/user/notifications/mark-as-read/<path:docname>",
                methods=["PUT"],
                endpoint=cls.mark_as_read(),
            ),
            Rule(
                "/user/notifications/mark-all-as-read",
                methods=["PUT"],
                endpoint=cls.mark_all_as_read(),
            ),
        ]
