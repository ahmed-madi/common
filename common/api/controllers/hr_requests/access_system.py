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
    "system_access_level",
    "status",
    "reason",
]
doctype = "System Access Request"


def access_system_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_access_system():
    return create_doc(doctype)


def read_access_system(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_access_system(name: str):
    return update_doc(doctype, name)


def delete_access_system(name: str):
    return delete_doc(doctype, name)
