from werkzeug.routing import Rule
from common.api.controllers.common.employee import employee_list, read_employee, employee_leave_balance

employee_rules = [
	Rule("/hr-common/employee", methods=["GET"], endpoint=employee_list),
	Rule("/hr-common/employee/<path:name>/", methods=["GET"], endpoint=read_employee),
	Rule("/hr-common/employee/<path:name>/leave-balance", methods=["GET"], endpoint=employee_leave_balance),
]