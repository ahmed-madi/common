from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = ["name", "employee", "leave_application", "return_date"]
doctype = "Leave Suspension"


def leave_suspension_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_leave_suspension():
    return create_doc(doctype)


def read_leave_suspension(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_leave_suspension(name: str):
    return update_doc(doctype, name)


def delete_leave_suspension(name: str):
    return delete_doc(doctype, name)
