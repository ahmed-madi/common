from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

fields = [
    "name",
    "request_date",
    "employee",
    "employee_name",
    "dependent_name",
    "status",
]
doctype = "Education Allowance Request"


def education_allowance_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_education_allowance():
    return create_doc(doctype)


def read_education_allowance(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_education_allowance(name: str):
    return update_doc(doctype, name)


def delete_education_allowance(name: str):
    return delete_doc(doctype, name)
