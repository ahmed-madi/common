from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "club_name"]


def club_list():
    doctype = "Club"
    return document_list(doctype, fields, translate_text=True, tr_field="club_name")


def read_club(name: str):
    doctype = "Club"
    return read_doc(doctype, name, origin_fields=fields)
