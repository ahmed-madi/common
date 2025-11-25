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
    "c_bank_name",
    "c_bank_ac_no",
    "c_iban",
    "bank_name",
    "bank_ac_no",
    "iban",
    "reason",
    "status",
]
doctype = "Change IBAN Request"


def change_iban_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_change_iban():
    return create_doc(doctype)


def read_change_iban(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_change_iban(name: str):
    return update_doc(doctype, name)


def delete_change_iban(name: str):
    return delete_doc(doctype, name)
