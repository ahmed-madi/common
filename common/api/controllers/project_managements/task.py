from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = [
    "name",
    "subject",
    "status",
    "priority",
    "assigned_to",
    "employee_name",
    "project",
    "exp_start_date",
    "exp_end_date",
]
doctype = "Task"


def task_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_task():
    return create_doc(doctype)


def read_task(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_task(name: str):
    return update_doc(doctype, name)


def delete_task(name: str):
    return delete_doc(doctype, name)
