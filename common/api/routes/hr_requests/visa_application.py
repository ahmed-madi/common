from werkzeug.routing import Rule
from common.api.controllers.hr_requests.visa_application import (
    visa_application_list,
    create_visa_application,
    read_visa_application,
    update_visa_application,
    delete_visa_application,
)

visa_application_rules = [
    Rule(
        "/hr-requests/visa-application", methods=["GET"], endpoint=visa_application_list
    ),
    Rule(
        "/hr-requests/visa-application",
        methods=["POST"],
        endpoint=create_visa_application,
    ),
    Rule(
        "/hr-requests/visa-application/<path:name>/",
        methods=["GET"],
        endpoint=read_visa_application,
    ),
    Rule(
        "/hr-requests/visa-application/<path:name>/",
        methods=["PUT"],
        endpoint=update_visa_application,
    ),
    Rule(
        "/hr-requests/visa-application/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_visa_application,
    ),
]
