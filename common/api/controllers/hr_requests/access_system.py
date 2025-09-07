from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

LIST_FIELDS = [
    "name",
    "request_date",
    "employee",
    "employee_name",
    "system_access_level",
    "status",
    "docstatus",
]
FROM_FIELDS = [] + LIST_FIELDS + ["reason"]


def access_system_list():
    doctype = "System Access Request"
    return document_list(doctype, LIST_FIELDS)


def create_access_system():
    doctype = "System Access Request"
    return create_doc(doctype)


def read_access_system(name: str):
    doctype = "System Access Request"
    return read_doc(doctype, name, origin_fields=FROM_FIELDS)


def update_access_system(name: str):
    doctype = "System Access Request"
    return update_doc(doctype, name)


def delete_access_system(name: str):
    doctype = "System Access Request"
    return delete_doc(doctype, name)
