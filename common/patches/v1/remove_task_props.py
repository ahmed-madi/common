import frappe


def execute():
    for ps in frappe.get_all(
        "Property Setter",
        filters={
            "doctype_or_field": "DocField",
            "doc_type": "Task",
            "property": "permlevel",
        },
    ):
        frappe.delete_doc("Property Setter", ps.name)
    for ps in frappe.get_all(
        "Property Setter",
        filters={
            "doctype_or_field": "DocField",
            "doc_type": "Task",
            "field_name": "status",
            "property": "options",
        },
    ):
        frappe.delete_doc("Property Setter", ps.name)
    frappe.db.commit()
