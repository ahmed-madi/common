from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def bonus_list():
    doctype = "Bonus Request"
    fields = ["*"]
    return document_list(doctype, fields)

def create_bonus():
    doctype = "Bonus Request"
    return create_doc(doctype)

def read_bonus(name: str):
    doctype = "Bonus Request"    
    return read_doc(doctype, name)


def update_bonus(name: str):
    doctype = "Bonus Request"
    return update_doc(doctype, name)


def delete_bonus(name: str):
    doctype = "Bonus Request"
    return delete_doc(doctype, name)
