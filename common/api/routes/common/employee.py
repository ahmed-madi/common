from werkzeug.routing import Rule
from common.api.controllers.common.employee import employee_list, read_employee

employee_rules = [
	Rule("/hr-common/employee", methods=["GET"], endpoint=employee_list),
	Rule("/hr-common/employee/<path:name>/", methods=["GET"], endpoint=read_employee),
]