from common.api.utils.resource import BaseResource

class TaskTimesheetLogResource(BaseResource):
    doctype = "Task Timesheet Log"
    url_prefix = "/project-managements"
    resource_name = "timesheet"
    fields = [
        "name",
        "task",
        "employee",
        "employee_name",
        "status",
        "posting_date",
        "start_time",
        "end_time",
        "total_hours",
        "project",
        "project_name",
        "description",
    ]
    add_perms = True
    add_wf = True
