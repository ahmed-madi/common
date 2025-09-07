from werkzeug.routing import Rule
from common.api.controllers.common.leave_type import leave_type_list, read_leave_type

leave_type_rules = [
    Rule("/hr-common/leave-type", methods=["GET"], endpoint=leave_type_list),
    Rule(
        "/hr-common/leave-type/<path:name>/", methods=["GET"], endpoint=read_leave_type
    ),
]
