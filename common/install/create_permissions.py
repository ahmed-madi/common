import frappe

DOCTYPE_LIST = [
    "Loan Product",
    "Department",
    "Holiday List",
    "Project Type",
    "Project",

    # Full Roles
    "Task",
]
ROLES = [
    "Employee",
    "Employee Self Service",
]

def create_custom_doc_perms():
    for doctype in DOCTYPE_LIST:
        for role in ROLES:
            exists = frappe.db.exists("Custom Role", {"role": role, "parent": doctype, "permlevel": 0})
            if exists:
                doc_perm = frappe.get_doc("Custom Role", exists)
            else:
                doc_perm = frappe.new_doc("Custom Role")
                doc_perm.update({
                    "role": role,
                    "parent": doctype,
                    "permlevel": 0,
                })
            doc_perm.update({
                "select": 1,
                "read": 1,
                "write": doctype in ["Task"],
                "create": doctype in ["Task"],
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "import": doctype in ["Task"],
                "share": 1,
                "print": 1,
                "email": 1,
            })
            doc_perm.save(ignore_permissions=True)