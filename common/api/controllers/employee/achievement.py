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
    "title",
    "date",
    "description",
    "attachment",
]
doctype = "Employee Achievement"


def achievement_list():
    return document_list(doctype, fields, add_perms=False, add_wf=False)


def create_achievement():
    return create_doc(doctype)


def read_achievement(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False)


def update_achievement(name: str):
    return update_doc(doctype, name)


def delete_achievement(name: str):
    return delete_doc(doctype, name)
