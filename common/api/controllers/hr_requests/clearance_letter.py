
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc
LIST_FIELDS = ["employee", "employee_name", "request_date", "letter_purpose", "clearance_document", "status", "docstatus"]
FORM_FIELDS = LIST_FIELDS + ["preferred_language", "remarks"]

def clearance_letter_list():
    doctype = "Clearance Letter Request"
    return document_list(doctype, LIST_FIELDS)

def create_clearance_letter():
    doctype = "Clearance Letter Request"
    return create_doc(doctype)

def read_clearance_letter(name: str):
    doctype = "Clearance Letter Request"    
    return read_doc(doctype, name, origin_fields=FORM_FIELDS)


def update_clearance_letter(name: str):
    doctype = "Clearance Letter Request"
    return update_doc(doctype, name)


def delete_clearance_letter(name: str):
    doctype = "Clearance Letter Request"
    return delete_doc(doctype, name)
