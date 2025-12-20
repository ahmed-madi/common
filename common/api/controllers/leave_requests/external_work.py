from common.api.utils.resource import BaseResource


class ExternalWorkResource(BaseResource):
    doctype = "Work Outside Office Request"
    url_prefix = "/leave-requests"
    resource_name = "external-work"
    fields = [
        "name",
        "employee",
        "employee_name",
        "request_date",
        "work_type",
        "from_date",
        "to_date",
        "status",
    ]
    add_perms = True
    add_wf = True
