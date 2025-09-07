from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)


def work_from_home_list():
    doctype = "Work From Home Request"
    fields = ["employee", "from_date", "to_date", "status", "docstatus"]
    return document_list(doctype, fields)


def create_work_from_home():
    doctype = "Work From Home Request"
    return create_doc(doctype)


def read_work_from_home(name: str):
    doctype = "Work From Home Request"
    fields = ["employee", "from_date", "to_date", "status", "docstatus"]
    return read_doc(doctype, name, origin_fields=fields)


def update_work_from_home(name: str):
    doctype = "Work From Home Request"
    return update_doc(doctype, name)


def delete_work_from_home(name: str):
    doctype = "Work From Home Request"
    return delete_doc(doctype, name)
