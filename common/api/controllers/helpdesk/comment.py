from werkzeug.routing import Rule
import frappe
from common.api.utils.resource import BaseResource
from common.api.utils.endpoints import document_list, create_doc, update_doc, delete_doc
from common.api.utils.decorators import safe_api

class TicketCommentResource(BaseResource):
    doctype = "HR Ticket Comment"
    url_prefix = "/helpdesk"
    resource_name = "ticket-comment"
    fields = [
        "name",
        "hr_ticket",
        "comment",
        "attachment",
        "parent_comment",
        "creation as created_at",
        "owner as created_by",
    ]
    
    @staticmethod
    def _verify_ticket(ticket):
        if not frappe.db.exists("HR Ticket", ticket):
            frappe.throw("Ticket not found", frappe.DoesNotExistError)
        # Permission logic could be added here if not handled by standard queries

    @classmethod
    def list(cls):
        @safe_api
        def _list(ticket):
            cls._verify_ticket(ticket)
            return document_list(
                cls.doctype,
                cls.fields,
                force_fields=True,
                user_filters={"hr_ticket": ticket},
                force_user_filters=True,
            )
        _list.__name__ = "ticket_comment_list"
        return _list

    @classmethod
    def create(cls):
        @safe_api
        def _create(ticket):
            cls._verify_ticket(ticket)
            default_data = {"hr_ticket": ticket}
            return create_doc(cls.doctype, default_data=default_data)
        _create.__name__ = "ticket_comment_create"
        return _create

    @classmethod
    def update(cls):
        @safe_api
        def _update(ticket, name):
            cls._verify_ticket(ticket)
            default_data = {"hr_ticket": ticket}
            return update_doc(cls.doctype, name, default_data=default_data)
        _update.__name__ = "ticket_comment_update"
        return _update

    @classmethod
    def delete(cls):
        @safe_api
        def _delete(ticket, name):
            cls._verify_ticket(ticket)
            return delete_doc(cls.doctype, name)
        _delete.__name__ = "ticket_comment_delete"
        return _delete

    @classmethod
    def get_routes(cls):
        base = f"{cls.url_prefix}/{cls.resource_name}"
        return [
            Rule(f"{base}/<path:ticket>/", methods=["GET"], endpoint=cls.list()),
            Rule(f"{base}/<path:ticket>/", methods=["POST"], endpoint=cls.create()),
            Rule(f"{base}/<path:ticket>/<path:name>/", methods=["PUT"], endpoint=cls.update()),
            Rule(f"{base}/<path:ticket>/<path:name>/", methods=["DELETE"], endpoint=cls.delete()),
        ]
