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
    "employee_name",
    "certificate_title",
    "issuing_organization",
    "date_of_issue",
    "attachment",
]
doctype = "Employee Certification"


def certification_list():
    return document_list(doctype, fields, add_perms=False, add_wf=False)


def read_certification(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False)


def create_certification():
    return create_doc(doctype)


def update_certification(name: str):
    return update_doc(doctype, name)


def delete_certification(name: str):
    return delete_doc(doctype, name)
