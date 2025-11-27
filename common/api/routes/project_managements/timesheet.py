from werkzeug.routing import Rule
from common.api.controllers.project_managements.timesheet import (
    timesheet_list,
    create_timesheet,
    read_timesheet,
    update_timesheet,
    delete_timesheet,
)

timesheet_rules = [
    Rule("/project-managements/timesheet", methods=["GET"], endpoint=timesheet_list),
    Rule("/project-managements/timesheet", methods=["POST"], endpoint=create_timesheet),
    Rule(
        "/project-managements/timesheet/<path:name>/",
        methods=["GET"],
        endpoint=read_timesheet,
    ),
    Rule(
        "/project-managements/timesheet/<path:name>/",
        methods=["PUT"],
        endpoint=update_timesheet,
    ),
    Rule(
        "/project-managements/timesheet/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_timesheet,
    ),
]
