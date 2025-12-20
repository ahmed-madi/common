from common.api.utils.resource import BaseResource


class EducationAllowanceRequestResource(BaseResource):
    doctype = "Education Allowance Request"
    url_prefix = "/hr-requests"
    resource_name = "education-allowance"
    fields = [
        "name",
        "employee",
        "employee_name",
        "request_date",
        "relation",
        "dependent_name",
        "attachment",
        "status",
    ]
    add_perms = True
    add_wf = True
