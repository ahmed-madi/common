import frappe


def execute():
    frappe.db.sql("""
        DELETE FROM `tabCustom Field`
        WHERE fieldname = 'assigned_to'
        AND dt = 'Task'
    """)
    frappe.db.sql("""
        DELETE FROM `tabProperty Setter`
        WHERE field_name = 'assigned_to'
        AND doc_type = 'Task'
    """)
