from werkzeug.routing import Rule
from common.api.controllers.hr_requests.employee_resignation import employee_resignation_list, create_employee_resignation, read_employee_resignation, update_employee_resignation, delete_employee_resignation

employee_resignation_rules = [
	Rule("/hr-requests/employee-resignation", methods=["GET"], endpoint=employee_resignation_list),
	Rule("/hr-requests/employee-resignation", methods=["POST"], endpoint=create_employee_resignation),
	Rule("/hr-requests/employee-resignation/<path:name>/", methods=["GET"], endpoint=read_employee_resignation),
	Rule("/hr-requests/employee-resignation/<path:name>/", methods=["PUT"], endpoint=update_employee_resignation),
	Rule("/hr-requests/employee-resignation/<path:name>/", methods=["DELETE"], endpoint=delete_employee_resignation),
]