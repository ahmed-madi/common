from common.api.utils.resource import BaseResource


class SalaryFixationResource(BaseResource):
    doctype = "Salary Fixation"
    url_prefix = "/hr-requests"
    resource_name = "salary-fixation"
    fields = [
        "name",
        "request_date",
        "effective_date",
        "employee",
        "employee_name",
        "fixation_reason",
        "salary_mode",
        "remarks",
        "status",
    ]
    add_perms = True
    add_wf = True
