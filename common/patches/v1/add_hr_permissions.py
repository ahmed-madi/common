import frappe

roles = ["Employee", "Employee Self Service"]
doctypes = [
    "Leave Application",
]


def execute():
    for doc in doctypes:
        for role in roles:
            exists = frappe.db.exists(
                "Custom DocPerm",
                {
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "parent": doc,
                    "role": role,
                    "permlevel": 0,
                },
            )
            if exists:
                perm_doc = frappe.get_doc("Custom DocPerm", exists)
            else:
                perm_doc = frappe.new_doc("Custom DocPerm")
            perm_doc.update(
                {
                    "parent": doc,
                    "role": role,
                    "permlevel": 0,
                    "read": 1,
                    "select": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                }
            )
            perm_doc.save()

            frappe.db.commit()
