import frappe
from frappe.utils import cint
from common.api.utils.endpoints import document_list, read_doc


fields = [
    "name",
    "subject",
    "published",
    "event_category",
    "color",
    "cover_image",
    "starts_on",
    "ends_on",
    "event_location",
    "status",
]
doctype = "Event"


def event_list():
    filters = [["published", "=", "1"]]
    if cint(frappe.db.get_single_value("Company Policy", "active_event_only")) == 1:
        filters.append(["status", "=", "Open"])
    return document_list(
        doctype,
        fields,
        user_filters=filters,
        force_user_filters=True,
        add_perms=False,
        add_wf=False,
    )


def read_event(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False)
