from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "language_name", "language_code", "flag", "based_on"]
doctype = "Language"


def language_list():
    return document_list(
        doctype,
        fields,
        user_filters=[["enabled", "=", 1]],
        force_user_filters=True,
        add_perms=False,
        add_wf=False,
    )


def read_language(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
