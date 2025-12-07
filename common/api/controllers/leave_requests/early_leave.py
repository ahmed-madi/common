from common.api.utils.resource import BaseResource

class EarlyLeaveResource(BaseResource):
    doctype = "Early Leave Application"
    url_prefix = "/leave-requests"
    resource_name = "early-leave"
    fields = ["name", "employee", "exit_date", "exit_time"]
    add_perms = True
    add_wf = True
