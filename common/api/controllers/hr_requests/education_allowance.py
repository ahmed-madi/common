from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)

LIST_FIELDS = [
    "name",
    "request_date",
    "employee",
    "employee_name",
    "dependent_name",
    "status",
    "docstatus",
]
FROM_FIELDS = (
    []
    + LIST_FIELDS
    + ["academic_year", "school_name", "amount_requested", "attachment", "remarks"]
)


def education_allowance_list():
    doctype = "Education Allowance Request"
    return document_list(doctype, LIST_FIELDS)


def create_education_allowance():
    doctype = "Education Allowance Request"
    return create_doc(doctype)


def read_education_allowance(name: str):
    doctype = "Education Allowance Request"
    return read_doc(doctype, name, origin_fields=FROM_FIELDS)


def update_education_allowance(name: str):
    doctype = "Education Allowance Request"
    return update_doc(doctype, name)


def delete_education_allowance(name: str):
    doctype = "Education Allowance Request"
    return delete_doc(doctype, name)
