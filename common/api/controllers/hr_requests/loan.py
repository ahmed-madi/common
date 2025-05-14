
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def loan_list():
    doctype = "Loan Request"
    fields = ["*"]
    return document_list(doctype, fields)

def create_loan():
    doctype = "Loan Request"
    return create_doc(doctype)

def read_loan(name: str):
    doctype = "Loan Request"    
    return read_doc(doctype, name)


def update_loan(name: str):
    doctype = "Loan Request"
    return update_doc(doctype, name)


def delete_loan(name: str):
    doctype = "Loan Request"
    return delete_doc(doctype, name)
