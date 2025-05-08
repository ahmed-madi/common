from werkzeug.routing import Rule
from common.api.controllers.leave_requests.early_leave import early_leave_list, create_early_leave, read_early_leave, update_early_leave, delete_early_leave

early_leave_rules = [
	Rule("/leave-requests/early-leave", methods=["GET"], endpoint=early_leave_list),
	Rule("/leave-requests/early-leave", methods=["POST"], endpoint=create_early_leave),
	Rule("/leave-requests/early-leave/<path:name>/", methods=["GET"], endpoint=read_early_leave),
	Rule("/leave-requests/early-leave/<path:name>/", methods=["PUT"], endpoint=update_early_leave),
	Rule("/leave-requests/early-leave/<path:name>/", methods=["DELETE"], endpoint=delete_early_leave),
]