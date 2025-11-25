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
    "leave_type",
    "from_date",
    "to_date",
    "total_leave_days",
    "status",
]

doctype = "Leave Application"


def leave_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_leave():
    return create_doc(doctype)


def read_leave(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_leave(name: str):
    return update_doc(doctype, name)


def delete_leave(name: str):
    return delete_doc(doctype, name)
