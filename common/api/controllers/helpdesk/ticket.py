from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

BASE_FIELDS = ["name", "subject", "opening_date", "opening_time", "department"]
FORM_FIELDS = BASE_FIELDS + [
    "employee",
    "priority",
    "issue_type",
    "phone",
    "description",
    "attachment",
]


def ticket_list():
    doctype = "HR Ticket"
    return document_list(doctype, BASE_FIELDS)


def create_ticket():
    doctype = "HR Ticket"
    return create_doc(doctype)


def read_ticket(name: str):
    doctype = "HR Ticket"
    return read_doc(doctype, name, origin_fields=FORM_FIELDS)


def update_ticket(name: str):
    doctype = "HR Ticket"
    return update_doc(doctype, name)


def delete_ticket(name: str):
    doctype = "HR Ticket"
    return delete_doc(doctype, name)
