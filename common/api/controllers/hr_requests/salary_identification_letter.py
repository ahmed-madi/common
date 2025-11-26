from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = [
    "name",
    "employee",
    "employee_name",
    "request_date",
    "recipient_name",
    "preferred_language",
    "signed_pdf_document",
    "status",
]
doctype = "Salary Identification Letter"


def salary_identification_letter_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_salary_identification_letter():
    return create_doc(doctype)


def read_salary_identification_letter(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_salary_identification_letter(name: str):
    return update_doc(doctype, name)


def delete_salary_identification_letter(name: str):
    return delete_doc(doctype, name)
