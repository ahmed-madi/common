from werkzeug.routing import Rule
from common.api.controllers.employee import employee_info, update_employee_info, achievement_list, create_achievement, update_achievement, delete_achievement, certification_list, create_certification, delete_certification, update_certification

employee_info_rules = [
    # Employee
	Rule("/employee/<path:employee>/", methods=["GET"], endpoint=employee_info),
	Rule("/employee/<path:employee>/", methods=["PUT"], endpoint=update_employee_info),

    # Employee Achievement
    Rule("/employee/<path:employee>/achievement", methods=["GET"], endpoint=achievement_list),
    Rule("/employee/<path:employee>/achievement", methods=["POST"], endpoint=create_achievement),
    Rule("/employee/<path:employee>/achievement/<path:name>", methods=["PUT"], endpoint=update_achievement),
    Rule("/employee/<path:employee>/achievement/<path:name>", methods=["DELETE"], endpoint=delete_achievement),

    # Employee Achievement
    Rule("/employee/<path:employee>/certification", methods=["GET"], endpoint=certification_list),
    Rule("/employee/<path:employee>/certification", methods=["POST"], endpoint=create_certification),
    Rule("/employee/<path:employee>/certification/<path:name>", methods=["PUT"], endpoint=update_certification),
    Rule("/employee/<path:employee>/certification/<path:name>", methods=["DELETE"], endpoint=delete_certification),
]