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
    "department",
    "feedback_type",
    "posting_date",
    "subject",
    "docstatus",
]
doctype = "Employee HR Feedback"


def employee_feedback_list():
    return document_list(doctype, fields, add_perms=True, add_wf=True)


def create_employee_feedback():
    return create_doc(doctype)


def read_employee_feedback(name: str):
    return read_doc(doctype, name, add_perms=True, add_wf=True)


def update_employee_feedback(name: str):
    return update_doc(doctype, name)


def delete_employee_feedback(name: str):
    return delete_doc(doctype, name)
