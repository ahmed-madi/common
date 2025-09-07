from werkzeug.routing import Rule
from common.api.controllers.leave_requests.work_from_home import (
    work_from_home_list,
    create_work_from_home,
    read_work_from_home,
    update_work_from_home,
    delete_work_from_home,
)

work_from_home_rules = [
    Rule(
        "/leave-requests/work-from-home", methods=["GET"], endpoint=work_from_home_list
    ),
    Rule(
        "/leave-requests/work-from-home",
        methods=["POST"],
        endpoint=create_work_from_home,
    ),
    Rule(
        "/leave-requests/work-from-home/<path:name>/",
        methods=["GET"],
        endpoint=read_work_from_home,
    ),
    Rule(
        "/leave-requests/work-from-home/<path:name>/",
        methods=["PUT"],
        endpoint=update_work_from_home,
    ),
    Rule(
        "/leave-requests/work-from-home/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_work_from_home,
    ),
]
