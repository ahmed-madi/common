from common.api.utils.resource import BaseResource


class VisaApplicationResource(BaseResource):
    doctype = "Visa Application"
    url_prefix = "/hr-requests"
    resource_name = "visa-application"
    fields = [
        "name",
        "employee",
        "employee_name",
        "request_date",
        "visa_type",
        "start_date",
        "end_date",
        "status",
    ]
    add_perms = True
    add_wf = True
