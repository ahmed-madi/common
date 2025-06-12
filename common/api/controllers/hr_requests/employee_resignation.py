
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

LIST_FIELDS = ["name", "request_date", "employee", "employee_name", "last_working_day", "status", "docstatus"]
FROM_FIELDS = [] + LIST_FIELDS + ["reasons_for_resignation"]

def employee_resignation_list():
    doctype = "Employee Resignation"
    return document_list(doctype, LIST_FIELDS)

def create_employee_resignation():
    doctype = "Employee Resignation"
    return create_doc(doctype)

def read_employee_resignation(name: str):
    doctype = "Employee Resignation"    
    return read_doc(doctype, name, origin_fields=FROM_FIELDS)


def update_employee_resignation(name: str):
    doctype = "Employee Resignation"
    return update_doc(doctype, name)


def delete_employee_resignation(name: str):
    doctype = "Employee Resignation"
    return delete_doc(doctype, name)
