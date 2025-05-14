
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def club_list():
    doctype = "Club Request"
    fields = ["*"]
    return document_list(doctype, fields)

def create_club():
    doctype = "Club Request"
    return create_doc(doctype)

def read_club(name: str):
    doctype = "Club Request"    
    return read_doc(doctype, name)


def update_club(name: str):
    doctype = "Club Request"
    return update_doc(doctype, name)


def delete_club(name: str):
    doctype = "Club Request"
    return delete_doc(doctype, name)
