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
    "training_title",
    "request_date",
    "start_date",
    "end_date",
    "status",
]
FORM_FIELDS = LIST_FIELDS + [
    "training_type",
    "training_provider",
    "training_duration",
    "is_paid",
    "training_price",
    "training_description",
]


def training_list():
    doctype = "Training Request"
    return document_list(doctype, LIST_FIELDS)


def create_training():
    doctype = "Training Request"
    return create_doc(doctype)


def read_training(name: str):
    doctype = "Training Request"
    return read_doc(doctype, name, origin_fields=FORM_FIELDS)


def update_training(name: str):
    doctype = "Training Request"
    return update_doc(doctype, name)


def delete_training(name: str):
    doctype = "Training Request"
    return delete_doc(doctype, name)
