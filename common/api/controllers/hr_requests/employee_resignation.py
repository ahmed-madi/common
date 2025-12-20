from common.api.utils.resource import BaseResource


class EmployeeResignationResource(BaseResource):
    doctype = "Employee Resignation"
    url_prefix = "/hr-requests"
    resource_name = "employee-resignation"
    fields = [
        "name",
        "employee",
        "employee_name",
        "request_date",
        "last_working_day",
        "status",
    ]
    add_perms = True
    add_wf = True
