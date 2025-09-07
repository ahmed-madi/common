from werkzeug.routing import Rule
from common.api.controllers.helpdesk.employee_feedback import (
    employee_feedback_list,
    create_employee_feedback,
    read_employee_feedback,
    update_employee_feedback,
    delete_employee_feedback,
)

employee_feedback_rules = [
    Rule(
        "/helpdesk/employee-feedback", methods=["GET"], endpoint=employee_feedback_list
    ),
    Rule(
        "/helpdesk/employee-feedback",
        methods=["POST"],
        endpoint=create_employee_feedback,
    ),
    Rule(
        "/helpdesk/employee-feedback/<path:name>/",
        methods=["GET"],
        endpoint=read_employee_feedback,
    ),
    Rule(
        "/helpdesk/employee-feedback/<path:name>/",
        methods=["PUT"],
        endpoint=update_employee_feedback,
    ),
    Rule(
        "/helpdesk/employee-feedback/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_employee_feedback,
    ),
]
