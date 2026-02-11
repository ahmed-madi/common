import frappe


def execute():
    properties_to_remove = frappe.get_all(
        "Property Setter",
        filters={"doc_type": "Task"},
        or_filters={
            "property": ["in", ["permlevel", "default"]],
            "field_name": "status",
        },
        pluck="name",
    )
    for p in properties_to_remove:
        frappe.delete_doc_if_exists("Property Setter", p, force=1)

    frappe.db.commit()
