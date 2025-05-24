from common.api.utils.endpoints import document_list, read_doc

def employee_list():
    doctype = "Employee"
    fields = ["name", "employee_name", "department", "designation", "date_of_joining"]
    return document_list(doctype, fields)

def read_employee(name: str):
    doctype = "Employee"
    fields = ["name", "employee_name", "department", "designation", "date_of_joining"]
    return read_doc(doctype, name, origin_fields=fields)

