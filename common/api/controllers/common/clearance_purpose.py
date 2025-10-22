from common.api.utils.endpoints import document_list, read_doc


fields = ["name", "purpose"]


def clearance_purpose_list():
    doctype = "Clearance Letter Purpose"
    return document_list(
        doctype, fields, force_fields=True, translate_text=True, tr_field="purpose"
    )


def read_clearance_purpose(name: str):
    doctype = "Clearance Letter Purpose"
    return read_doc(doctype, name, origin_fields=fields, force_fields=True)
