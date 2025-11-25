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
    "fixation_reason",
    "salary_mode",
    "bank_name",
    "employee_iban",
    "remarks",
    "effective_date",
    "bank_name",
    "remarks",
    "status",
]
doctype = "Salary Fixation"


def salary_fixation_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_salary_fixation():
    return create_doc(doctype)


def read_salary_fixation(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_salary_fixation(name: str):
    return update_doc(doctype, name)


def delete_salary_fixation(name: str):
    return delete_doc(doctype, name)
