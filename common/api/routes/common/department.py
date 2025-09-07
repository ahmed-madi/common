from werkzeug.routing import Rule
from common.api.controllers.common.department import department_list, read_department

department_rules = [
    Rule("/hr-common/department", methods=["GET"], endpoint=department_list),
    Rule(
        "/hr-common/department/<path:name>/", methods=["GET"], endpoint=read_department
    ),
]
