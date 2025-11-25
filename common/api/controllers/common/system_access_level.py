from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "access_level"]
doctype = "System Access Level"


def system_access_level_list():
    return document_list(
        doctype,
        fields,
        add_perms=False,
        add_wf=False,
    )


def read_system_access_level(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
