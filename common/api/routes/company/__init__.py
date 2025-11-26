from werkzeug.routing import Rule
from common.api.controllers.company.activity import activity_list
from common.api.controllers.company.event import event_list, read_event
from common.api.controllers.company.newsletter import newsletter_list, read_newsletter
from common.api.controllers.company.organizational_chart import (
    department_structure,
    employee_structure,
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
