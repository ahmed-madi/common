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
    "document_type",
    "document_language",
    "status",
]
doctype = "Document Request"


def document_request_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_document_request():
    return create_doc(doctype)


def read_document_request(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_document_request(name: str):
    return update_doc(doctype, name)


def delete_document_request(name: str):
    return delete_doc(doctype, name)
