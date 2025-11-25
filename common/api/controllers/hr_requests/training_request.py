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
    "training_title",
    "request_date",
    "start_date",
    "end_date",
    "status",
]
doctype = "Training Request"


def training_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_training():
    return create_doc(doctype)


def read_training(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_training(name: str):
    return update_doc(doctype, name)


def delete_training(name: str):
    return delete_doc(doctype, name)
