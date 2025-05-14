from werkzeug.routing import Rule
from common.api.controllers.hr_requests.training import training_list, create_training, read_training, update_training, delete_training

training_rules = [
	Rule("/hr-requests/training", methods=["GET"], endpoint=training_list),
	Rule("/hr-requests/training", methods=["POST"], endpoint=create_training),
	Rule("/hr-requests/training/<path:name>/", methods=["GET"], endpoint=read_training),
	Rule("/hr-requests/training/<path:name>/", methods=["PUT"], endpoint=update_training),
	Rule("/hr-requests/training/<path:name>/", methods=["DELETE"], endpoint=delete_training),
]