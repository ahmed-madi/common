from werkzeug.routing import Rule
from common.api.controllers.common.holiday_list import (
    holiday_list_list,
    read_holiday_list,
)

holiday_list_rules = [
    Rule("/hr-common/holiday-list", methods=["GET"], endpoint=holiday_list_list),
    Rule(
        "/hr-common/holiday-list/<path:name>/",
        methods=["GET"],
        endpoint=read_holiday_list,
    ),
]
