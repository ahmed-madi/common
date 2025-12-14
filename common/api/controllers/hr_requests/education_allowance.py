from common.api.utils.resource import BaseResource

class EducationAllowanceRequestResource(BaseResource):
    doctype = "Education Allowance Request"
    url_prefix = "/hr-requests"
    resource_name = "education-allowance"
    fields = ["name", "request_date", "employee", "employee_name", "dependent_name", "status"]
    add_perms = True
    add_wf = True
