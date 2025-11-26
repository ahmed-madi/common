from werkzeug.routing import Rule

from common.api.controllers.employee.certification import (
    certification_list,
    create_certification,
    read_certification,
    update_certification,
    delete_certification,
)
from common.api.controllers.employee.achievement import (
    achievement_list,
    create_achievement,
    read_achievement,
    update_achievement,
    delete_achievement,
)

from common.api.controllers.employee.attendance import (
    create_checkin,
    attendance_list,
    check_in_out_list,
)
from common.api.controllers.employee.info import (
    update_employee_info,
    employee_info,
    other_employee_info,
)

from common.api.controllers.employee.salary_slip import download_salary_slip

employee_info_rules = [
    # Employee
    Rule("/employee/<path:employee>/", methods=["GET"], endpoint=employee_info),
    Rule(
        "/employee-info/<path:employee>/", methods=["GET"], endpoint=other_employee_info
    ),
    Rule(
        "/employee/<path:employee>/download-slip/<path:name>",
        methods=["GET"],
        endpoint=download_salary_slip,
    ),
    # Done!!!!!!
    Rule("/employee/<path:employee>/", methods=["PUT"], endpoint=update_employee_info),
    Rule("/employee/checkin", methods=["POST"], endpoint=create_checkin),
    Rule("/employee/checkin", methods=["GET"], endpoint=check_in_out_list),
    Rule(
        "/employee/attendance",
        methods=["GET"],
        endpoint=attendance_list,
    ),
    Rule(
        "/employee/achievement",
        methods=["GET"],
        endpoint=achievement_list,
    ),
    Rule(
        "/employee/achievement",
        methods=["POST"],
        endpoint=create_achievement,
    ),
    Rule(
        "/employee/achievement/<path:name>",
        methods=["GET"],
        endpoint=read_achievement,
    ),
    Rule(
        "/employee/achievement/<path:name>",
        methods=["PUT"],
        endpoint=update_achievement,
    ),
    Rule(
        "/employee/achievement/<path:name>",
        methods=["DELETE"],
        endpoint=delete_achievement,
    ),
    Rule(
        "/employee/certification",
        methods=["GET"],
        endpoint=certification_list,
    ),
    Rule(
        "/employee/certification",
        methods=["POST"],
        endpoint=create_certification,
    ),
    Rule(
        "/employee/certification/<path:name>",
        methods=["GET"],
        endpoint=read_certification,
    ),
    Rule(
        "/employee/certification/<path:name>",
        methods=["PUT"],
        endpoint=update_certification,
    ),
    Rule(
        "/employee/certification/<path:name>",
        methods=["DELETE"],
        endpoint=delete_certification,
    ),
]
