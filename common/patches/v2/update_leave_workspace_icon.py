import frappe


def execute():
    if not frappe.db.exists("Workspace", "Leaves"):
        return
    frappe.db.set_value("Workspace", "Leaves", "icon", "palm-tree")
