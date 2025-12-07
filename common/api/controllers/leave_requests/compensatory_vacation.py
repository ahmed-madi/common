from common.api.utils.resource import BaseResource

class CompensatoryVacationResource(BaseResource):
    doctype = "Compensatory Leave Request"
    url_prefix = "/leave-requests"
    resource_name = "compensatory-vacation"
    fields = ["name", "employee", "leave_type", "status"]
    add_perms = True
    add_wf = True
