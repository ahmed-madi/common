from werkzeug.routing import Rule
from common.api.controllers.leave_requests.external_work import external_work_list, create_external_work, read_external_work, update_external_work, delete_external_work

external_work_rules = [
	Rule("/leave-requests/external-work", methods=["GET"], endpoint=external_work_list),
	Rule("/leave-requests/external-work", methods=["POST"], endpoint=create_external_work),
	Rule("/leave-requests/external-work/<path:name>/", methods=["GET"], endpoint=read_external_work),
	Rule("/leave-requests/external-work/<path:name>/", methods=["PUT"], endpoint=update_external_work),
	Rule("/leave-requests/external-work/<path:name>/", methods=["DELETE"], endpoint=delete_external_work),
]