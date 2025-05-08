
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def leave_suspension_list():
    doctype = "Leave Suspension"
    fields = ["name", "employee", "leave_application", "return_date"]
    return document_list(doctype, fields)

def create_leave_suspension():
    doctype = "Leave Suspension"
    return create_doc(doctype)

def read_leave_suspension(name: str):
    doctype = "Leave Suspension"
    fields = ["name", "employee", "leave_application", "return_date"]
    return read_doc(doctype, name, origin_fields=fields)


def update_leave_suspension(name: str):
    doctype = "Leave Suspension"
    return update_doc(doctype, name)


def delete_leave_suspension(name: str):
    doctype = "Leave Suspension"
    return delete_doc(doctype, name)
