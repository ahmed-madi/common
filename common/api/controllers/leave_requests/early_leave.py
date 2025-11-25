from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = ["name", "employee", "exit_date", "exit_time"]
doctype = "Early Leave Application"


def early_leave_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_early_leave():
    return create_doc(doctype)


def read_early_leave(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_early_leave(name: str):
    return update_doc(doctype, name)


def delete_early_leave(name: str):
    return delete_doc(doctype, name)
