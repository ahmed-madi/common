
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

LIST_FIELDS = ["name", "request_date", "employee", "employee_name", "management_area", "subject", "docstatus"]
FROM_FIELDS = [] + LIST_FIELDS + ["message", "attachment"]

def request_to_management_list():
    doctype = "Request to Management"
    return document_list(doctype, LIST_FIELDS)

def create_request_to_management():
    doctype = "Request to Management"
    return create_doc(doctype)

def read_request_to_management(name: str):
    doctype = "Request to Management"
    return read_doc(doctype, name, origin_fields=FROM_FIELDS)


def update_request_to_management(name: str):
    doctype = "Request to Management"
    return update_doc(doctype, name)


def delete_request_to_management(name: str):
    doctype = "Request to Management"
    return delete_doc(doctype, name)
