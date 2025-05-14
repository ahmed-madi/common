from werkzeug.routing import Rule
from common.api.controllers.hr_requests.education_allowance import education_allowance_list, create_education_allowance, read_education_allowance, update_education_allowance, delete_education_allowance

education_allowance_rules = [
	Rule("/hr-requests/education-allowance", methods=["GET"], endpoint=education_allowance_list),
	Rule("/hr-requests/education-allowance", methods=["POST"], endpoint=create_education_allowance),
	Rule("/hr-requests/education-allowance/<path:name>/", methods=["GET"], endpoint=read_education_allowance),
	Rule("/hr-requests/education-allowance/<path:name>/", methods=["PUT"], endpoint=update_education_allowance),
	Rule("/hr-requests/education-allowance/<path:name>/", methods=["DELETE"], endpoint=delete_education_allowance),
]