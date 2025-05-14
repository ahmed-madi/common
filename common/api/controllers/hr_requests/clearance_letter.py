
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def clearance_letter_list():
    doctype = "Clearance Letter Request"
    fields = ["*"]
    return document_list(doctype, fields)

def create_clearance_letter():
    doctype = "Clearance Letter Request"
    return create_doc(doctype)

def read_clearance_letter(name: str):
    doctype = "Clearance Letter Request"    
    return read_doc(doctype, name)


def update_clearance_letter(name: str):
    doctype = "Clearance Letter Request"
    return update_doc(doctype, name)


def delete_clearance_letter(name: str):
    doctype = "Clearance Letter Request"
    return delete_doc(doctype, name)
