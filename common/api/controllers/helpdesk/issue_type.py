
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def compensatory_vacation_list():
    doctype = "HR Ticket Comment"
    fields = ["name", "employee", "leave_type", "status"]
    return document_list(doctype, fields)

def create_compensatory_vacation():
    doctype = "HR Ticket Comment"
    return create_doc(doctype)

def read_compensatory_vacation(name: str):
    doctype = "HR Ticket Comment"
    fields = ["name", "employee", "leave_type", "status"]    
    return read_doc(doctype, name, origin_fields=fields)


def update_compensatory_vacation(name: str):
    doctype = "HR Ticket Comment"
    return update_doc(doctype, name)


def delete_compensatory_vacation(name: str):
    doctype = "HR Ticket Comment"
    return delete_doc(doctype, name)
