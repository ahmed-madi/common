from werkzeug.routing import Rule
from common.api.controllers.helpdesk.comment import (
    ticket_comment_list,
    create_ticket_comment,
    update_ticket_comment,
    delete_ticket_comment,
)

ticket_comment_rules = [
    Rule(
        "/helpdesk/ticket-comment/<path:ticket>/",
        methods=["GET"],
        endpoint=ticket_comment_list,
    ),
    Rule(
        "/helpdesk/ticket-comment/<path:ticket>/",
        methods=["POST"],
        endpoint=create_ticket_comment,
    ),
    Rule(
        "/helpdesk/ticket-comment/<path:ticket>/<path:name>/",
        methods=["PUT"],
        endpoint=update_ticket_comment,
    ),
    Rule(
        "/helpdesk/ticket-comment/<path:ticket>/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_ticket_comment,
    ),
]
