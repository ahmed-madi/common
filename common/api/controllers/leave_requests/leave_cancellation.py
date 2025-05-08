
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def leave_cancellation_list():
    doctype = "Cancel Leave Application"
    fields = ["name", "employee", "request_date", "leave_application"]
    return document_list(doctype, fields)

def create_leave_cancellation():
    doctype = "Cancel Leave Application"
    return create_doc(doctype)

def read_leave_cancellation(name: str):
    doctype = "Cancel Leave Application"
    fields = ["name", "employee", "request_date", "leave_application"]   
    return read_doc(doctype, name, origin_fields=fields)


def update_leave_cancellation(name: str):
    doctype = "Cancel Leave Application"
    return update_doc(doctype, name)


def delete_leave_cancellation(name: str):
    doctype = "Cancel Leave Application"
    return delete_doc(doctype, name)
