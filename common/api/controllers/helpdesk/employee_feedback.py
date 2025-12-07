from common.api.utils.resource import BaseResource

class EmployeeHRFeedbackResource(BaseResource):
    doctype = "Employee HR Feedback"
    url_prefix = "/helpdesk"
    resource_name = "employee-feedback"
    fields = [
        "name",
        "employee",
        "employee_name",
        "department",
        "feedback_type",
        "posting_date",
        "subject",
        "docstatus",
    ]
    add_perms = True
    add_wf = True
