from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

LIST_FIELDS = [
    "name",
    "employee",
    "employee_name",
    "department",
    "feedback_type",
    "posting_date",
    "subject",
    "docstatus",
]
FROM_FIELDS = LIST_FIELDS + ["message", "attachment"]


def employee_feedback_list():
    doctype = "Employee HR Feedback"
    return document_list(doctype, LIST_FIELDS)


def create_employee_feedback():
    doctype = "Employee HR Feedback"
    return create_doc(doctype)


def read_employee_feedback(name: str):
    doctype = "Employee HR Feedback"
    return read_doc(doctype, name, origin_fields=FROM_FIELDS)


def update_employee_feedback(name: str):
    doctype = "Employee HR Feedback"
    return update_doc(doctype, name)


def delete_employee_feedback(name: str):
    doctype = "Employee HR Feedback"
    return delete_doc(doctype, name)
