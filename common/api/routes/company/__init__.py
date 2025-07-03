from werkzeug.routing import Rule
from common.api.controllers.company import event_list, read_event, employee_structure, department_structure

company_rules = [
	Rule("/company/event", methods=["GET"], endpoint=event_list),
	Rule("/company/event/<path:name>/", methods=["GET"], endpoint=read_event),

	Rule("/company/employee-structure", methods=["GET"], endpoint=employee_structure),
	Rule("/company/department-structure", methods=["GET"], endpoint=department_structure),
]