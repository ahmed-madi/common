from werkzeug.routing import Rule
from common.api.controllers.project_managements.task import (
    task_list,
    create_task,
    read_task,
    update_task,
    delete_task,
)

task_rules = [
    Rule("/project-managements/task", methods=["GET"], endpoint=task_list),
    Rule("/project-managements/task", methods=["POST"], endpoint=create_task),
    Rule("/project-managements/task/<path:name>/", methods=["GET"], endpoint=read_task),
    Rule(
        "/project-managements/task/<path:name>/", methods=["PUT"], endpoint=update_task
    ),
    Rule(
        "/project-managements/task/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_task,
    ),
]
