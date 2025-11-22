from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "club_name"]
doctype = "Club"


def club_list():
    return document_list(doctype, fields)


def read_club(name: str):
    return read_doc(doctype, name)
