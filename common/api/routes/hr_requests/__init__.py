from werkzeug.routing import Rule
from common.api.controllers.hr_requests import (
    employee_requests_list,
    employee_requests_state_list,
)

employee_requests_rules = [
    Rule(
        "/employee-requests-status",
        methods=["GET"],
        endpoint=employee_requests_state_list,
    ),
    Rule("/employee-requests", methods=["GET"], endpoint=employee_requests_list),
]
