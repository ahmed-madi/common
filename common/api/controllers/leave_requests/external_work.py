from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = ["name", "employee", "from_date", "to_date", "status"]
doctype = "Work Outside Office Request"


def external_work_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_external_work():
    return create_doc(doctype)


def read_external_work(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_external_work(name: str):
    return update_doc(doctype, name)


def delete_external_work(name: str):
    return delete_doc(doctype, name)
