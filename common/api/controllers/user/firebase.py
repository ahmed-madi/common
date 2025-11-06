import frappe
from frappe.utils import cint

from common.api.utils import get_request_form_data
from common.api.utils.endpoints import (
    create_doc,
)
from common.api.utils.response import build_success_response, build_error_response


# test workflow
@frappe.whitelist()
def get_config():
    try:
        doc = frappe.get_doc("FCM Settings")
        if cint(doc.enable) == 0:
            return build_error_response(
                403, "Failed to fetch FCM configurations", "FCM Feature is not enabled"
            )

        data = {
            "enable": doc.enable,
            "config": {
                "apiKey": doc.api_key,
                "authDomain": doc.auth_domain,
                "projectId": doc.project_id,
                "storageBucket": doc.storage_bucket,
                "messagingSenderId": doc.messaging_sender_id,
                "appId": doc.app_id,
            },
            "key_pair": doc.key_pair,
        }
        build_success_response(
            status_code=200, message="FCM configurations fetched", data=data
        )
    except:  # noqa: E722
        build_error_response(
            403, "Failed to fetch FCM configurations", frappe.get_traceback()
        )


# Subscribe and Unsubscribe API
@frappe.whitelist(methods=["POST"])
def subscribe():
    doctype = "FCM Device Token"
    frappe.delete_doc(
        "FCM Device Token", {"user": frappe.session.user}, ignore_permissions=True
    )
    return create_doc(doctype, default_data={"user": frappe.session.user})


@frappe.whitelist(methods=["DELETE"])
def unsubscribe():
    fcm_token = get_request_form_data().get("token")
    for dt in frappe.get_all("FCM Device Token", filters={"token": fcm_token}):
        frappe.delete_doc("FCM Device Token", dt.name, force=True)
    frappe.db.commit()
    build_success_response(status_code=200, message="FCM Token Deleted", data={})


@frappe.whitelist(methods=["GET"])
def get_user_settings():
    try:
        user = frappe.get_doc("User", frappe.session.user)
        if not user.has_permission("read"):
            raise frappe.PermissionError
        user.apply_fieldlevel_read_permissions()

        exists = frappe.db.exists(
            "HR Notification Settings", {"user": frappe.session.user}
        )
        if exists:
            doc = frappe.get_doc("HR Notification Settings", exists)
        else:
            doc = frappe.new_doc("HR Notification Settings")
            doc.update(
                {
                    "user": frappe.session.user,
                    "task_assignments": 1,
                    "request_approvals": 1,
                    "calendar_events": 1,
                    "helpdesk_updates": 1,
                    "performance_reviews": 1,
                }
            )
            doc.save(ignore_permissions=True)
            frappe.db.commit()
        terms_and_conditions_ar = frappe.db.get_single_value(
            "Company Policy", "terms_and_conditions_ar"
        )
        terms_and_conditions_en = frappe.db.get_single_value(
            "Company Policy", "terms_and_conditions_en"
        )
        doc = {
            "user": doc.user,
            "task_assignments": doc.task_assignments,
            "request_approvals": doc.request_approvals,
            "calendar_events": doc.calendar_events,
            "helpdesk_updates": doc.helpdesk_updates,
            "performance_reviews": doc.performance_reviews,
            "language": user.language,
            "theme": user.desk_theme,
            "terms_and_conditions_ar": terms_and_conditions_ar,
            "terms_and_conditions_en": terms_and_conditions_en,
        }

        return build_success_response(200, "user settings fetched", doc, {})
    except Exception as exc:
        http_status_code = 500
        message = exc
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 0 and isinstance(args[0], str):
                message = args[0].split(":")[0]
            elif len(args) > 1 and isinstance(args[0], int):
                message = args[1]
        return build_error_response(
            http_status_code, "failed to read user settings", message
        )


@frappe.whitelist(methods=["POST"])
def update_user_settings():
    try:
        data = get_request_form_data()
        doc1 = set_notification_settings(data, frappe.session.user)
        doc2 = set_user_settings(data, frappe.session.user)
        doc1.update(doc2)
        return build_success_response(200, "user settings updated", doc1)
    except Exception as exc:
        http_status_code = 500
        message = exc
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 0 and isinstance(args[0], str):
                message = args[0].split(":")[0]
            elif len(args) > 1 and isinstance(args[0], int):
                message = args[1]
        return build_error_response(
            http_status_code, "failed to update user settings", message
        )


def set_notification_settings(data, user):
    if (
        "task_assignments" not in data
        and "request_approvals" not in data
        and "calendar_events" not in data
        and "helpdesk_updates" not in data
        and "performance_reviews" not in data
    ):
        return

    exists = frappe.db.exists("HR Notification Settings", {"user": user})
    if exists:
        doc = frappe.get_doc("HR Notification Settings", exists)
    else:
        doc = frappe.new_doc("HR Notification Settings")
        doc.update(
            {
                "user": frappe.session.user,
                "task_assignments": 1,
                "request_approvals": 1,
                "calendar_events": 1,
                "helpdesk_updates": 1,
                "performance_reviews": 1,
            }
        )
    if "task_assignments" in data:
        doc.update(
            {
                "task_assignments": cint(data.get("task_assignments")),
            }
        )
    if "request_approvals" in data:
        doc.update(
            {
                "request_approvals": cint(data.get("request_approvals")),
            }
        )
    if "calendar_events" in data:
        doc.update(
            {
                "calendar_events": cint(data.get("calendar_events")),
            }
        )
    if "helpdesk_updates" in data:
        doc.update(
            {
                "helpdesk_updates": cint(data.get("helpdesk_updates")),
            }
        )
    if "performance_reviews" in data:
        doc.update(
            {
                "performance_reviews": cint(data.get("performance_reviews")),
            }
        )
    doc.save(ignore_permissions=True)
    return {
        "user": doc.user,
        "task_assignments": doc.task_assignments,
        "request_approvals": doc.request_approvals,
        "calendar_events": doc.calendar_events,
        "helpdesk_updates": doc.helpdesk_updates,
        "performance_reviews": doc.performance_reviews,
    }


def set_user_settings(data, user):
    if "language" not in data and "theme" not in data:
        return
    exists = frappe.db.exists("User", {"name": user})
    if not exists:
        return
    user = frappe.get_doc("User", exists)
    if "language" in data:
        user.update(
            {
                "language": data.get("language"),
            }
        )
    if "theme" in data:
        user.update(
            {
                "desk_theme": data.get("theme"),
            }
        )
    user.save(ignore_permissions=True)
    return {
        "language": user.language,
        "theme": user.desk_theme,
    }
