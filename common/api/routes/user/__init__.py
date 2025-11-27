from werkzeug.routing import Rule
from common.api.utils.endpoints import handle_call, build_success_response
from common.api.controllers.user import (
    notification_list,
    mark_as_read as mark_notification_as_read,
)


def login():
    return handle_call("common.api.controllers.user.login")


def logout():
    return handle_call("common.api.controllers.user.logout")


def refresh_token():
    return handle_call("common.api.controllers.user.refresh_token")


def user_info():
    return handle_call("common.api.controllers.user.user_info")


def change_user_password():
    return handle_call("common.api.controllers.user.change_user_password")


def mark_all_as_read():
    handle_call(
        "frappe.desk.doctype.notification_log.notification_log.mark_all_as_read"
    )
    return build_success_response(200, "All Notification marked as Read", data={})


def mark_as_read(docname):
    mark_notification_as_read(docname)


user_rules = [
    Rule("/user/auth/login", methods=["POST"], endpoint=login),
    Rule("/user/auth/logout", methods=["POST"], endpoint=logout),
    Rule("/user/auth/refresh-token", methods=["POST"], endpoint=refresh_token),
    Rule("/user/change-password", methods=["PUT"], endpoint=change_user_password),
    Rule("/user/info", methods=["GET"], endpoint=user_info),
    Rule("/user/notifications", methods=["GET"], endpoint=notification_list),
    Rule(
        "/user/notifications/mark-as-read/<path:docname>",
        methods=["PUT"],
        endpoint=mark_as_read,
    ),
    Rule(
        "/user/notifications/mark-all-as-read",
        methods=["PUT"],
        endpoint=mark_all_as_read,
    ),
]
