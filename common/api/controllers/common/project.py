from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "project_name", "priority", "status", "is_active"]
doctype = "Project"


def project_list():
    return document_list(
        doctype,
        fields,
        add_perms=False,
        add_wf=False,
    )


def read_project(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
