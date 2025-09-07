from werkzeug.routing import Rule
from common.api.controllers.hr_requests.change_iban import (
    change_iban_list,
    create_change_iban,
    read_change_iban,
    update_change_iban,
    delete_change_iban,
)

change_iban_rules = [
    Rule("/hr-requests/change-iban", methods=["GET"], endpoint=change_iban_list),
    Rule("/hr-requests/change-iban", methods=["POST"], endpoint=create_change_iban),
    Rule(
        "/hr-requests/change-iban/<path:name>/",
        methods=["GET"],
        endpoint=read_change_iban,
    ),
    Rule(
        "/hr-requests/change-iban/<path:name>/",
        methods=["PUT"],
        endpoint=update_change_iban,
    ),
    Rule(
        "/hr-requests/change-iban/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_change_iban,
    ),
]
