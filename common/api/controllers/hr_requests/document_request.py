from common.api.utils.resource import BaseResource

class DocumentRequestResource(BaseResource):
    doctype = "Document Request"
    url_prefix = "/hr-requests"
    resource_name = "document-request"
    fields = ["name", "employee", "employee_name", "request_date", "document_type", "document_language", "status"]
    add_perms = True
    add_wf = True
