from common.api.utils.resource import BaseResource


class SystemAccessRequestResource(BaseResource):
    doctype = "System Access Request"
    url_prefix = "/hr-requests"
    resource_name = "access-system"
    fields = [
        "name",
        "employee",
        "employee_name",
        "request_date",
        "system_access_level",
        "reason",
        "status",
    ]
    add_perms = True
    add_wf = True
