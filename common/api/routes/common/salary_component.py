from werkzeug.routing import Rule
from common.api.controllers.common.salary_component import salary_component_list, read_salary_component

salary_component_rules = [
	Rule("/hr-common/salary-component", methods=["GET"], endpoint=salary_component_list),
	Rule("/hr-common/salary-component/<path:name>/", methods=["GET"], endpoint=read_salary_component),
]