from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "project_name", "priority", "status", "is_active"]


def project_list():
    doctype = "Project"
    return document_list(doctype, fields, translate_text=True, tr_field="project_name")


def read_project(name: str):
    doctype = "Project"
    return read_doc(doctype, name, origin_fields=fields)
