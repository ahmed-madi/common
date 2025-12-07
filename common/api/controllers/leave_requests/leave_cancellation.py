from common.api.utils.resource import BaseResource

class LeaveCancellationResource(BaseResource):
    doctype = "Cancel Leave Application"
    url_prefix = "/leave-requests"
    resource_name = "leave-cancellation"
    fields = ["name", "employee", "request_date", "leave_application"]
    add_perms = True
    add_wf = True
