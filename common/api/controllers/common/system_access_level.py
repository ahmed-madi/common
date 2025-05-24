from common.api.utils.endpoints import document_list, read_doc

def system_access_level_list():
    doctype = "System Access Level"
    fields = ["name", "access_level"]
    return document_list(doctype, fields)

def read_system_access_level(name: str):
    doctype = "System Access Level"
    fields = ["name", "access_level"]
    return read_doc(doctype, name, origin_fields=fields)
