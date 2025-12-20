from common.api.utils.resource import BaseResource


class EmployeeExpenseRequestResource(BaseResource):
    doctype = "Employee Expense Request"
    url_prefix = "/hr-requests"
    resource_name = "expenses-request"
    fields = [
        "name",
        "request_type",
        "expenses_type",
        "employee",
    ]
    add_perms = True
    add_wf = True
