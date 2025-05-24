from werkzeug.routing import Rule
from common.api.controllers.hr_requests.training_request import training_list, create_training, read_training, update_training, delete_training

training_request_rules = [
	Rule("/hr-requests/training-request", methods=["GET"], endpoint=training_list),
	Rule("/hr-requests/training-request", methods=["POST"], endpoint=create_training),
	Rule("/hr-requests/training-request/<path:name>/", methods=["GET"], endpoint=read_training),
	Rule("/hr-requests/training-request/<path:name>/", methods=["PUT"], endpoint=update_training),
	Rule("/hr-requests/training-request/<path:name>/", methods=["DELETE"], endpoint=delete_training),
]