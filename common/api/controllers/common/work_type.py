from common.api.utils.endpoints import document_list, read_doc


def work_type_list():
    doctype = "Work Type"
    fields = ["name", "type"]
    return document_list(doctype, fields, translate_text=True, tr_field="type")


def read_work_type(name: str):
    doctype = "Work Type"
    fields = ["name", "type"]
    return read_doc(doctype, name, origin_fields=fields)
