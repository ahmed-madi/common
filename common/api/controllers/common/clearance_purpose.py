from common.api.utils.endpoints import document_list, read_doc


fields = ["name", "purpose"]
doctype = "Clearance Letter Purpose"


def clearance_purpose_list():
    return document_list(doctype, fields, add_perms=False, add_wf=False)


def read_clearance_purpose(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
