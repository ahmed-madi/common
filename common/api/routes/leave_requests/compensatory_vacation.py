from werkzeug.routing import Rule
from common.api.controllers.leave_requests.compensatory_vacation import (
    compensatory_vacation_list,
    create_compensatory_vacation,
    read_compensatory_vacation,
    update_compensatory_vacation,
    delete_compensatory_vacation,
)

compensatory_vacation_rules = [
    Rule(
        "/leave-requests/compensatory-vacation",
        methods=["GET"],
        endpoint=compensatory_vacation_list,
    ),
    Rule(
        "/leave-requests/compensatory-vacation",
        methods=["POST"],
        endpoint=create_compensatory_vacation,
    ),
    Rule(
        "/leave-requests/compensatory-vacation/<path:name>/",
        methods=["GET"],
        endpoint=read_compensatory_vacation,
    ),
    Rule(
        "/leave-requests/compensatory-vacation/<path:name>/",
        methods=["PUT"],
        endpoint=update_compensatory_vacation,
    ),
    Rule(
        "/leave-requests/compensatory-vacation/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_compensatory_vacation,
    ),
]
