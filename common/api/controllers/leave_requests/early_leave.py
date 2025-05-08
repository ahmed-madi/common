
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def early_leave_list():
    doctype = "Early Leave Application"
    fields = ["name", "employee", "exit_date", "exit_time"]
    return document_list(doctype, fields)

def create_early_leave():
    doctype = "Early Leave Application"
    return create_doc(doctype)

def read_early_leave(name: str):
    doctype = "Early Leave Application"    
    fields = ["name", "employee", "exit_date", "exit_time"]
    return read_doc(doctype, name, origin_fields=fields)


def update_early_leave(name: str):
    doctype = "Early Leave Application"
    return update_doc(doctype, name)


def delete_early_leave(name: str):
    doctype = "Early Leave Application"
    return delete_doc(doctype, name)
