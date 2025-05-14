from werkzeug.routing import Rule
from common.api.controllers.hr_requests.access_system import access_system_list, create_access_system, read_access_system, update_access_system, delete_access_system

access_system_rules = [
	Rule("/hr-requests/access-system", methods=["GET"], endpoint=access_system_list),
	Rule("/hr-requests/access-system", methods=["POST"], endpoint=create_access_system),
	Rule("/hr-requests/access-system/<path:name>/", methods=["GET"], endpoint=read_access_system),
	Rule("/hr-requests/access-system/<path:name>/", methods=["PUT"], endpoint=update_access_system),
	Rule("/hr-requests/access-system/<path:name>/", methods=["DELETE"], endpoint=delete_access_system),
]