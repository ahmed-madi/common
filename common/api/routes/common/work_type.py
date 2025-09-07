from werkzeug.routing import Rule
from common.api.controllers.common.work_type import work_type_list, read_work_type

work_type_rules = [
    Rule("/hr-common/work-type", methods=["GET"], endpoint=work_type_list),
    Rule("/hr-common/work-type/<path:name>/", methods=["GET"], endpoint=read_work_type),
]
