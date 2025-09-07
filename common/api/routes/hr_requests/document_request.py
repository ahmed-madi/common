from werkzeug.routing import Rule
from common.api.controllers.hr_requests.document_request import (
    document_request_list,
    create_document_request,
    read_document_request,
    update_document_request,
    delete_document_request,
)

document_request_rules = [
    Rule(
        "/hr-requests/document-request", methods=["GET"], endpoint=document_request_list
    ),
    Rule(
        "/hr-requests/document-request",
        methods=["POST"],
        endpoint=create_document_request,
    ),
    Rule(
        "/hr-requests/document-request/<path:name>/",
        methods=["GET"],
        endpoint=read_document_request,
    ),
    Rule(
        "/hr-requests/document-request/<path:name>/",
        methods=["PUT"],
        endpoint=update_document_request,
    ),
    Rule(
        "/hr-requests/document-request/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_document_request,
    ),
]
