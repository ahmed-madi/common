import frappe

roles = ["Employee", "Employee Self Service", "HR User", "Direct Manager"]
doctypes = [
    "Holiday List", "Loan Product",
]


def execute():
    for doc in doctypes:
        for role in roles:
            if frappe.db.exists(
                "Custom DocPerm",
                {
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "parent": doc,
                    "role": role,
                    "permlevel": 1,
                    "read": 0,
                },
            ):
                continue

            perm_doc = frappe.new_doc("Custom DocPerm")
            perm_doc.update(
                {
                    "parent": doc,
                    "role": role,
                    "permlevel": 0,
                    "read": 1,
                }
            )
            perm_doc.save()

            frappe.db.commit()
