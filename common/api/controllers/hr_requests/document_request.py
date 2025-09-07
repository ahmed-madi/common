from common.api.utils.endpoints import (
    document_list,
    create_doc,
    read_doc,
    update_doc,
    delete_doc,
)


def document_request_list():
    doctype = "Document Request"
    fields = ["*"]
    return document_list(doctype, fields)


def create_document_request():
    doctype = "Document Request"
    return create_doc(doctype)


def read_document_request(name: str):
    doctype = "Document Request"
    return read_doc(doctype, name)


def update_document_request(name: str):
    doctype = "Document Request"
    return update_doc(doctype, name)


def delete_document_request(name: str):
    doctype = "Document Request"
    return delete_doc(doctype, name)
