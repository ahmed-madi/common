from werkzeug.routing import Rule
from common.api.controllers.leave_requests.leave_cancellation import (
    leave_cancellation_list,
    create_leave_cancellation,
    read_leave_cancellation,
    update_leave_cancellation,
    delete_leave_cancellation,
)

leave_cancellation_rules = [
    Rule(
        "/leave-requests/leave-cancellation",
        methods=["GET"],
        endpoint=leave_cancellation_list,
    ),
    Rule(
        "/leave-requests/leave-cancellation",
        methods=["POST"],
        endpoint=create_leave_cancellation,
    ),
    Rule(
        "/leave-requests/leave-cancellation/<path:name>/",
        methods=["GET"],
        endpoint=read_leave_cancellation,
    ),
    Rule(
        "/leave-requests/leave-cancellation/<path:name>/",
        methods=["PUT"],
        endpoint=update_leave_cancellation,
    ),
    Rule(
        "/leave-requests/leave-cancellation/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_leave_cancellation,
    ),
]
