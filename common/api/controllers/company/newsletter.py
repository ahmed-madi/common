from common.api.utils.endpoints import document_list, read_doc


fields = [
    "name",
    "subject",
    "publish_on",
    "cover_image",
    "published",
    "cover_image",
    "intro_description",
    "list_image",
]
doctype = "Company Newsletter"


def newsletter_list():
    filters = [["published", "=", "1"]]
    return document_list(
        doctype,
        fields,
        user_filters=filters,
        force_user_filters=True,
        add_perms=False,
        add_wf=False,
    )


def read_newsletter(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False)
