from werkzeug.routing import Rule
from common.api.controllers.leave_requests.leave import leave_list, create_leave, read_leave, update_leave, delete_leave

leave_application_rules = [
	Rule("/leave-requests/leave-application", methods=["GET"], endpoint=leave_list),
	Rule("/leave-requests/leave-application", methods=["POST"], endpoint=create_leave),
	Rule("/leave-requests/leave-application/<path:name>/", methods=["GET"], endpoint=read_leave),
	Rule("/leave-requests/leave-application/<path:name>/", methods=["PUT"], endpoint=update_leave),
	Rule("/leave-requests/leave-application/<path:name>/", methods=["DELETE"], endpoint=delete_leave),
]