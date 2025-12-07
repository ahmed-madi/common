from common.api.utils.resource import BaseResource

class WorkFromHomeResource(BaseResource):
    doctype = "Work From Home Request"
    url_prefix = "/leave-requests"
    resource_name = "work-from-home"
    fields = ["employee", "from_date", "to_date", "status", "docstatus"]
    add_perms = True
    add_wf = True
