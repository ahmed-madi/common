import frappe


def execute():
    properties_to_remove = frappe.get_all(
        "Property Setter",
        {"doc_type": "Task", "property": ["in", ["permlevel", "default"]]},
        pluck="name",
    ) + ["Task-status-options"]
    for p in properties_to_remove:
        frappe.delete_doc_if_exists("Property Setter", p, force=1)

    frappe.db.commit()
