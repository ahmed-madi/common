import frappe
from frappe import _


def translate_link_fields(doctype, data):
    meta = frappe.get_meta(doctype)
    lang = frappe.db.get_value("User", frappe.session.user, "language")
    if lang == "en":
        return
    for field in meta.get_link_fields():
        if field.fieldname not in data:
            continue
        data.update({f"{field.fieldname}": _(data.get(field.fieldname), lang=lang)})
