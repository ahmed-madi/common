from common.api.utils.resource import BaseResource


class GeneralRequestResource(BaseResource):
    doctype = "General Request"
    url_prefix = "/hr-requests"
    resource_name = "general-request"
    fields = [
        "name",
        "employee",
        "employee_name",
        "department",
        "request_date",
        "request_type",
        "title",
        "message",
        "attachment",
    ]
    add_perms = True
    add_wf = False
