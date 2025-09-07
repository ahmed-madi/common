from werkzeug.routing import Rule
from common.api.controllers.common.project import project_list, read_project

project_rules = [
    Rule("/hr-common/project", methods=["GET"], endpoint=project_list),
    Rule("/hr-common/project/<path:name>/", methods=["GET"], endpoint=read_project),
]
