
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def education_allowance_list():
    doctype = "Education Allowance Request"
    fields = ["*"]
    return document_list(doctype, fields)

def create_education_allowance():
    doctype = "Education Allowance Request"
    return create_doc(doctype)

def read_education_allowance(name: str):
    doctype = "Education Allowance Request"    
    return read_doc(doctype, name)


def update_education_allowance(name: str):
    doctype = "Education Allowance Request"
    return update_doc(doctype, name)


def delete_education_allowance(name: str):
    doctype = "Education Allowance Request"
    return delete_doc(doctype, name)
