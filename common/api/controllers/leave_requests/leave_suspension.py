from common.api.utils.resource import BaseResource

class LeaveSuspensionResource(BaseResource):
    doctype = "Leave Suspension"
    url_prefix = "/leave-requests"
    resource_name = "leave-suspension"
    fields = ["name", "employee", "leave_application", "return_date"]
    add_perms = True
    add_wf = True
