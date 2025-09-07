from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

LIST_FIELDS = [
    "name",
    "applicant",
    "applicant_name",
    "posting_date",
    "loan_product",
    "status",
    "docstatus",
]
FORM_FIELDS = LIST_FIELDS + [
    "is_term_loan",
    "loan_purpose",
    "attachment",
    "repayment_method",
    "repayment_amount",
    "repayment_periods",
]


def loan_list():
    doctype = "Loan Application"
    return document_list(doctype, fields=LIST_FIELDS)


def create_loan():
    doctype = "Loan Application"
    return create_doc(doctype)


def read_loan(name: str):
    doctype = "Loan Application"
    return read_doc(doctype, name, origin_fields=FORM_FIELDS)


def update_loan(name: str):
    doctype = "Loan Application"
    return update_doc(doctype, name)


def delete_loan(name: str):
    doctype = "Loan Application"
    return delete_doc(doctype, name)
