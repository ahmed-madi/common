
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc
LIST_FIELDS = ["name", "employee", "employee_name","request_date", "start_date", "end_date", "status"]
FORM_FIELDS = LIST_FIELDS + ["participation_role", "is_paid", "participation_price", "remarks", "attachment"]

def club_list():
    doctype = "Club Request"
    return document_list(doctype, LIST_FIELDS)

def create_club():
    doctype = "Club Request"
    return create_doc(doctype)

def read_club(name: str):
    doctype = "Club Request"
    return read_doc(doctype, name, origin_fields=FORM_FIELDS)


def update_club(name: str):
    doctype = "Club Request"
    return update_doc(doctype, name)


def delete_club(name: str):
    doctype = "Club Request"
    return delete_doc(doctype, name)
