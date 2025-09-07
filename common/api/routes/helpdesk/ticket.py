from werkzeug.routing import Rule
from common.api.controllers.helpdesk.ticket import (
    ticket_list,
    create_ticket,
    read_ticket,
    update_ticket,
    delete_ticket,
)

ticket_rules = [
    Rule("/helpdesk/ticket", methods=["GET"], endpoint=ticket_list),
    Rule("/helpdesk/ticket", methods=["POST"], endpoint=create_ticket),
    Rule("/helpdesk/ticket/<path:name>/", methods=["GET"], endpoint=read_ticket),
    Rule("/helpdesk/ticket/<path:name>/", methods=["PUT"], endpoint=update_ticket),
    Rule("/helpdesk/ticket/<path:name>/", methods=["DELETE"], endpoint=delete_ticket),
]
