import frappe
from frappe.utils import cint

from common.api.utils import get_request_form_data
from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
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
    except:
        build_error_response(
            403, "Failed to fetch FCM configurations", frappe.get_traceback()
        )


# Subscribe and Unsubscribe API
@frappe.whitelist(methods=["POST"])
def subscribe():
    doctype = "FCM Device Token"
    return create_doc(doctype, default_data={"user": frappe.session.user})


@frappe.whitelist(methods=["DELETE"])
def unsubscribe():
    fcm_token = get_request_form_data().get("token")
    for dt in frappe.get_all("FCM Device Token", filters={"token": fcm_token}):
        frappe.delete_doc("FCM Device Token", dt.name, force=True)
    frappe.db.commit()
    build_success_response(status_code=200, message="FCM Token Deleted", data={})


@frappe.whitelist(methods=["POST"])
def update_notifications_settings():
    data = get_request_form_data()
    exists = frappe.db.exists("HR Notification Settings", {"user": frappe.session.user})
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
