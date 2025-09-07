from werkzeug.routing import Rule
from common.api.controllers.hr_requests.clearance_letter import (
    clearance_letter_list,
    create_clearance_letter,
    read_clearance_letter,
    update_clearance_letter,
    delete_clearance_letter,
)

clearance_letter_rules = [
    Rule(
        "/hr-requests/clearance-letter", methods=["GET"], endpoint=clearance_letter_list
    ),
    Rule(
        "/hr-requests/clearance-letter",
        methods=["POST"],
        endpoint=create_clearance_letter,
    ),
    Rule(
        "/hr-requests/clearance-letter/<path:name>/",
        methods=["GET"],
        endpoint=read_clearance_letter,
    ),
    Rule(
        "/hr-requests/clearance-letter/<path:name>/",
        methods=["PUT"],
        endpoint=update_clearance_letter,
    ),
    Rule(
        "/hr-requests/clearance-letter/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_clearance_letter,
    ),
]
