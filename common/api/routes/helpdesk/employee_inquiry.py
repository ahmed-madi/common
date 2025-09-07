from werkzeug.routing import Rule
from common.api.controllers.helpdesk.employee_inquiry import (
    request_to_management_list,
    create_request_to_management,
    read_request_to_management,
    update_request_to_management,
    delete_request_to_management,
)

request_to_management_rules = [
    Rule(
        "/helpdesk/employee-inquiry",
        methods=["GET"],
        endpoint=request_to_management_list,
    ),
    Rule(
        "/helpdesk/employee-inquiry",
        methods=["POST"],
        endpoint=create_request_to_management,
    ),
    Rule(
        "/helpdesk/employee-inquiry/<path:name>/",
        methods=["GET"],
        endpoint=read_request_to_management,
    ),
    Rule(
        "/helpdesk/employee-inquiry/<path:name>/",
        methods=["PUT"],
        endpoint=update_request_to_management,
    ),
    Rule(
        "/helpdesk/employee-inquiry/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_request_to_management,
    ),
]
