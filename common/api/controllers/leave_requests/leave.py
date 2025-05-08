
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def leave_list():
    doctype = "Leave Application"
    fields = ["*"]
    return document_list(doctype, fields)

def create_leave():
    doctype = "Leave Application"
    return create_doc(doctype)

def read_leave(name: str):
    doctype = "Leave Application"    
    return read_doc(doctype, name)


def update_leave(name: str):
    doctype = "Leave Application"
    return update_doc(doctype, name)


def delete_leave(name: str):
    doctype = "Leave Application"
    return delete_doc(doctype, name)
