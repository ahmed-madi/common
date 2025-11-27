from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = ["name", "subject", "status", "opening_date", "opening_time", "department"]
doctype = "HR Ticket"


def ticket_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_ticket():
    return create_doc(doctype)


def read_ticket(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_ticket(name: str):
    return update_doc(doctype, name)


def delete_ticket(name: str):
    return delete_doc(doctype, name)
