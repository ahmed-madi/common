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
    "last_working_day",
    "status",
]
doctype = "Employee Resignation"


def employee_resignation_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_employee_resignation():
    return create_doc(doctype)


def read_employee_resignation(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_employee_resignation(name: str):
    return update_doc(doctype, name)


def delete_employee_resignation(name: str):
    return delete_doc(doctype, name)
