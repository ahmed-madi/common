
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

LIST_FIELDS = ["name", "request_date", "employee", "employee_name", "c_bank_name", "c_bank_ac_no", "c_iban", "bank_name", "bank_ac_no", "iban", "reason", "status", "docstatus"]
FROM_FIELDS = [] + LIST_FIELDS + ["reason", "attachment"]

def change_iban_list():
    doctype = "Change IBAN Request"
    return document_list(doctype, LIST_FIELDS)

def create_change_iban():
    doctype = "Change IBAN Request"
    return create_doc(doctype)

def read_change_iban(name: str):
    doctype = "Change IBAN Request"
    return read_doc(doctype, name, origin_fields=FROM_FIELDS)


def update_change_iban(name: str):
    doctype = "Change IBAN Request"
    return update_doc(doctype, name)


def delete_change_iban(name: str):
    doctype = "Change IBAN Request"
    return delete_doc(doctype, name)
