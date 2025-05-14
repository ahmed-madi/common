
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def training_list():
    doctype = "Training Request"
    fields = ["*"]
    return document_list(doctype, fields)

def create_training():
    doctype = "Training Request"
    return create_doc(doctype)

def read_training(name: str):
    doctype = "Training Request"    
    return read_doc(doctype, name)


def update_training(name: str):
    doctype = "Training Request"
    return update_doc(doctype, name)


def delete_training(name: str):
    doctype = "Training Request"
    return delete_doc(doctype, name)
