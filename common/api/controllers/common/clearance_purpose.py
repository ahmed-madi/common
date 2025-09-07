from common.api.utils.endpoints import document_list, read_doc


def clearance_purpose_list():
    doctype = "Clearance Letter Purpose"
    fields = ["name"]
    return document_list(doctype, fields, force_fields=True)


def read_clearance_purpose(name: str):
    doctype = "Clearance Letter Purpose"
    fields = ["name"]
    return read_doc(doctype, name, origin_fields=fields, force_fields=True)
