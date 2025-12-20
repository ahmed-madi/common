from common.api.utils.resource import BaseResource


class CompensatoryVacationResource(BaseResource):
    doctype = "Compensatory Leave Request"
    url_prefix = "/leave-requests"
    resource_name = "compensatory-vacation"
    fields = [
        "name",
        "employee",
        "employee_name",
        "request_date",
        "work_from_date",
        "work_end_date",
        "leave_type",
        "status",
    ]
    add_perms = True
    add_wf = True
