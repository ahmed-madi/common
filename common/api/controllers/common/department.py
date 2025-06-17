from common.api.utils.endpoints import document_list, read_doc
fields = ["name", "department_name", "disabled"]

def department_list():
    doctype = "Department"
    return document_list(doctype, fields, force_fields=True)

def read_department(name: str):
    doctype = "Department"
    return read_doc(doctype, name, origin_fields=fields, force_fields=True)

