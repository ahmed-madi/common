import frappe


def execute():
    frappe.db.sql("UPDATE `tabTask` SET assigned_to=custom_employee")
    frappe.db.commit()
