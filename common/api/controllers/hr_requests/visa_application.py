from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

BASE_FIELDS = [
    "name",
    "employee",
    "request_date",
    "visa_type",
    "start_date",
    "end_date",
    "status",
    "docstatus",
]
FORM_FIELDS = BASE_FIELDS + ["remarks", "attachment"]


def visa_application_list():
    doctype = "Visa Application"
    return document_list(doctype, BASE_FIELDS)


def create_visa_application():
    doctype = "Visa Application"
    return create_doc(doctype)


def read_visa_application(name: str):
    doctype = "Visa Application"
    return read_doc(doctype, name, origin_fields=FORM_FIELDS)


def update_visa_application(name: str):
    doctype = "Visa Application"
    return update_doc(doctype, name)


def delete_visa_application(name: str):
    doctype = "Visa Application"
    return delete_doc(doctype, name)
