import frappe
from common.api.utils.endpoints import document_list, create_doc, update_doc ,delete_doc
from common.api.controllers.helpdesk.ticket import read_ticket
def ticket_comment_list(ticket: str):
    read_ticket(ticket)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "HR Ticket Comment"
    filters = {
        "hr_ticket": ticket
    }
    fields = ["name", "hr_ticket", "comment", "attachment", "parent_comment", "creation as created_at", "owner as created_by"]
    return document_list(doctype, fields, force_fields=True, user_filters=filters)

def create_ticket_comment(ticket):
    read_ticket(ticket)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "HR Ticket Comment"
    default_data = {
        "hr_ticket": ticket
    }
    return create_doc(doctype, default_data=default_data)

def update_ticket_comment(ticket: str, name: str):
    read_ticket(ticket)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "HR Ticket Comment"
    default_data = {
        "hr_ticket": ticket
    }
    return update_doc(doctype, name, default_data=default_data)

def delete_ticket_comment(ticket: str, name: str):
    read_ticket(ticket)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "HR Ticket Comment"
    return delete_doc(doctype, name)
