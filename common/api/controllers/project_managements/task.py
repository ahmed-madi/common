from common.api.utils.resource import BaseResource


class TaskResource(BaseResource):
    doctype = "Task"
    url_prefix = "/project-managements"
    resource_name = "task"
    fields = [
        "name",
        "subject",
        "status",
        "priority",
        "assigned_to",  # employee
        "employee_name",
        "project",
        "exp_start_date",
        "exp_end_date",
    ]
    add_perms = True
    add_wf = True
