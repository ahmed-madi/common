from common.api.utils.resource import BaseResource

class SalaryFixationResource(BaseResource):
    doctype = "Salary Fixation"
    url_prefix = "/hr-requests"
    resource_name = "salary-fixation"
    fields = ["name", "employee", "employee_name", "fixation_reason", "salary_mode", "bank_name", "employee_iban", "remarks", "effective_date", "bank_name", "remarks", "status"]
    add_perms = True
    add_wf = True
