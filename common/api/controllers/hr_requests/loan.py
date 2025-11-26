from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = [
    "name",
    "applicant",
    "applicant_name",
    "posting_date",
    "loan_product",
    "status",
]
doctype = "Loan Application"


def loan_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_loan():
    return create_doc(doctype)


def read_loan(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_loan(name: str):
    return update_doc(doctype, name)


def delete_loan(name: str):
    return delete_doc(doctype, name)
