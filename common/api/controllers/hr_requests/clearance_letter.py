from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = [
    "name",
    "employee",
    "employee_name",
    "request_date",
    "letter_purpose",
    "clearance_document",
    "status",
]
doctype = "Clearance Letter Request"


def clearance_letter_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_clearance_letter():
    return create_doc(doctype)


def read_clearance_letter(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_clearance_letter(name: str):
    return update_doc(doctype, name)


def delete_clearance_letter(name: str):
    return delete_doc(doctype, name)
