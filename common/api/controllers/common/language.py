from common.api.utils.endpoints import document_list, read_doc
fields = ["name", "language_name", "enabled"]

def language_list():
    doctype = "Language"
    return document_list(doctype, fields)

def read_language(name: str):
    doctype = "Language"
    return read_doc(doctype, name, origin_fields=fields)

