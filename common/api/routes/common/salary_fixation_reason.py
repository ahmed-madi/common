from werkzeug.routing import Rule
from common.api.controllers.common.salary_fixation_reason import salary_fixation_reason_list, read_salary_fixation_reason

salary_fixation_reason_rules = [
	Rule("/hr-common/salary-fixation-reason", methods=["GET"], endpoint=salary_fixation_reason_list),
	Rule("/hr-common/salary-fixation-reason/<path:name>/", methods=["GET"], endpoint=read_salary_fixation_reason),
]