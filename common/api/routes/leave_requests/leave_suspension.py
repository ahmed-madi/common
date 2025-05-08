from werkzeug.routing import Rule
from common.api.controllers.leave_requests.leave_suspension import leave_suspension_list, create_leave_suspension, read_leave_suspension, update_leave_suspension, delete_leave_suspension

leave_suspension_rules = [
	Rule("/leave-requests/leave-suspension", methods=["GET"], endpoint=leave_suspension_list),
	Rule("/leave-requests/leave-suspension", methods=["POST"], endpoint=create_leave_suspension),
	Rule("/leave-requests/leave-suspension/<path:name>/", methods=["GET"], endpoint=read_leave_suspension),
	Rule("/leave-requests/leave-suspension/<path:name>/", methods=["PUT"], endpoint=update_leave_suspension),
	Rule("/leave-requests/leave-suspension/<path:name>/", methods=["DELETE"], endpoint=delete_leave_suspension),
]