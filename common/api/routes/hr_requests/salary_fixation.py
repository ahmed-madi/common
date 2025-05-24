from werkzeug.routing import Rule
from common.api.controllers.hr_requests.salary_fixation import salary_fixation_list, create_salary_fixation, read_salary_fixation, update_salary_fixation, delete_salary_fixation

salary_fixation_rules = [
	Rule("/hr-requests/salary-fixation", methods=["GET"], endpoint=salary_fixation_list),
	Rule("/hr-requests/salary-fixation", methods=["POST"], endpoint=create_salary_fixation),
	Rule("/hr-requests/salary-fixation/<path:name>/", methods=["GET"], endpoint=read_salary_fixation),
	Rule("/hr-requests/salary-fixation/<path:name>/", methods=["PUT"], endpoint=update_salary_fixation),
	Rule("/hr-requests/salary-fixation/<path:name>/", methods=["DELETE"], endpoint=delete_salary_fixation),
]