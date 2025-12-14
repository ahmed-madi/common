from common.api.utils.resource import BaseResource

class EmployeeResignationResource(BaseResource):
    doctype = "Employee Resignation"
    url_prefix = "/hr-requests"
    resource_name = "employee-resignation"
    fields = ["name", "request_date", "employee", "employee_name", "last_working_day", "status"]
    add_perms = True
    add_wf = True
