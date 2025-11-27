from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = [
    "name",
    "request_date",
    "employee",
    "employee_name",
    "management_area",
    "subject",
    "docstatus",
]
doctype = "Employee Inquiry"


def request_to_management_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_request_to_management():
    return create_doc(doctype)


def read_request_to_management(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_request_to_management(name: str):
    return update_doc(doctype, name)


def delete_request_to_management(name: str):
    return delete_doc(doctype, name)
