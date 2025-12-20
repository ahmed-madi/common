from common.api.utils.resource import BaseResource


class EmployeeInquiryResource(BaseResource):
    doctype = "Employee Inquiry"
    url_prefix = "/helpdesk"
    resource_name = "employee-inquiry"
    fields = [
        "name",
        "request_date",
        "employee",
        "employee_name",
        "management_area",
        "subject",
    ]
    add_perms = True
    add_wf = True
