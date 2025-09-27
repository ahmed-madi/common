from werkzeug.routing import Rule
from common.api.controllers.company import (
    event_list,
    read_event,
    employee_structure,
    department_structure,
    newsletter_list,
    read_newsletter,
    activity_list,
)

company_rules = [
    Rule("/company/newsletter", methods=["GET"], endpoint=newsletter_list),
    Rule("/company/newsletter/<path:name>/", methods=["GET"], endpoint=read_newsletter),
    Rule("/company/event", methods=["GET"], endpoint=event_list),
    Rule("/company/event/<path:name>/", methods=["GET"], endpoint=read_event),
    Rule("/company/activities", methods=["GET"], endpoint=activity_list),
    Rule("/company/employee-structure", methods=["GET"], endpoint=employee_structure),
    Rule(
        "/company/department-structure", methods=["GET"], endpoint=department_structure
    ),
]
