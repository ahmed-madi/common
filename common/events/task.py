import frappe


def on_update(doc, method=None):
    share_task(doc)


def share_task(doc):
    prev_doc = doc.get_doc_before_save() or {}
    if doc.get("custom_employee") == prev_doc.get("custom_employee"):
        return

    user_id = frappe.get_cached_value("Employee", doc.get("custom_employee"), "user_id")
    prev_user_id = frappe.get_cached_value(
        "Employee", prev_doc.get("custom_employee"), "user_id"
    )

    if user_id == doc.owner:
        return

    # share task with employee
    frappe.share.remove(doc.doctype, doc.name, prev_user_id)
    frappe.share.add(doc.doctype, doc.name, user_id)
