from common.api.utils.resource import BaseResource

class ClearanceLetterRequestResource(BaseResource):
    doctype = "Clearance Letter Request"
    url_prefix = "/hr-requests"
    resource_name = "clearance-letter"
    fields = ["name", "employee", "employee_name", "request_date", "letter_purpose", "clearance_document", "status"]
    add_perms = True
    add_wf = True
