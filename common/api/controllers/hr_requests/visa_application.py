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
    "request_date",
    "visa_type",
    "start_date",
    "end_date",
    "status",
]
doctype = "Visa Application"

def visa_application_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_visa_application():
    return create_doc(doctype)


def read_visa_application(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_visa_application(name: str):
    return update_doc(doctype, name)


def delete_visa_application(name: str):
    return delete_doc(doctype, name)
