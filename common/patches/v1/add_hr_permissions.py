import frappe


def execute():
    from common.install.create_permissions import create_custom_doc_perms

    create_custom_doc_perms()
    frappe.db.commit()
