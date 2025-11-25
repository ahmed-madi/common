from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = ["employee", "from_date", "to_date", "status", "docstatus"]
doctype = "Work From Home Request"


def work_from_home_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_work_from_home():
    return create_doc(doctype)


def read_work_from_home(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_work_from_home(name: str):
    return update_doc(doctype, name)


def delete_work_from_home(name: str):
    return delete_doc(doctype, name)
