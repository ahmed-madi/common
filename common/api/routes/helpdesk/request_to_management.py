from werkzeug.routing import Rule
from common.api.controllers.helpdesk.request_to_management import request_to_management_list, create_request_to_management, read_request_to_management, update_request_to_management, delete_request_to_management

request_to_management_rules = [
	Rule("/hr-requests/request-to-management", methods=["GET"], endpoint=request_to_management_list),
	Rule("/hr-requests/request-to-management", methods=["POST"], endpoint=create_request_to_management),
	Rule("/hr-requests/request-to-management/<path:name>/", methods=["GET"], endpoint=read_request_to_management),
	Rule("/hr-requests/request-to-management/<path:name>/", methods=["PUT"], endpoint=update_request_to_management),
	Rule("/hr-requests/request-to-management/<path:name>/", methods=["DELETE"], endpoint=delete_request_to_management),
]