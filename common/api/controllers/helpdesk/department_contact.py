from common.api.utils.resource import BaseResource


class DepartmentContactResource(BaseResource):
    doctype = "Department Contact"
    url_prefix = "/helpdesk"
    resource_name = "department-contact"
    fields = [
        "name",
        "request_date",
        "department",
        "subject",
        "message",
        "from_employee",
        "employee_name",
        "employee_department",
        "replay_to",
        "is_replay",
    ]
    add_perms = False
    add_wf = False
