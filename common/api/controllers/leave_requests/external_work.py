from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)


def external_work_list():
    doctype = "Work Outside Office Request"
    fields = ["name", "employee", "from_date", "to_date", "status"]
    return document_list(doctype, fields)


def create_external_work():
    doctype = "Work Outside Office Request"
    return create_doc(doctype)


def read_external_work(name: str):
    doctype = "Work Outside Office Request"
    fields = ["name", "employee", "from_date", "to_date", "status"]
    return read_doc(doctype, name, origin_fields=fields)


def update_external_work(name: str):
    doctype = "Work Outside Office Request"
    return update_doc(doctype, name)


def delete_external_work(name: str):
    doctype = "Work Outside Office Request"
    return delete_doc(doctype, name)
