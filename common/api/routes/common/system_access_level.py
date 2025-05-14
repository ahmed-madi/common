from werkzeug.routing import Rule
from common.api.controllers.common.system_access_level import system_access_level_list, read_system_access_level

system_access_level_rules = [
	Rule("/hr-common/system-access-level", methods=["GET"], endpoint=system_access_level_list),
	Rule("/hr-common/system-access-level/<path:name>/", methods=["GET"], endpoint=read_system_access_level),
]