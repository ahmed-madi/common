from werkzeug.routing import Rule
from common.api.controllers.common.clearance_purpose import (
    clearance_purpose_list,
    read_clearance_purpose,
)

clearance_purpose_rules = [
    Rule(
        "/hr-common/clearance-purpose", methods=["GET"], endpoint=clearance_purpose_list
    ),
    Rule(
        "/hr-common/clearance-purpose/<path:name>/",
        methods=["GET"],
        endpoint=read_clearance_purpose,
    ),
]
