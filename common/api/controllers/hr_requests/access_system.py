from common.api.utils.resource import BaseResource

class SystemAccessRequestResource(BaseResource):
    doctype = "System Access Request"
    url_prefix = "/hr-requests"
    resource_name = "access-system"
    fields = ["name", "request_date", "employee", "employee_name", "system_access_level", "status", "reason"]
    add_perms = True
    add_wf = True
