from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "type"]
doctype = "Work Type"


def work_type_list():
    return document_list(
        doctype,
        fields,
        add_perms=False,
        add_wf=False,
    )


def read_work_type(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
