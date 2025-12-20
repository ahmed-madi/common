import frappe

EMPLOYEE_ROLES = [
    "Employee",
    "Employee Self Service",
]

MANAGER_ROLES = [
    "HR Manager",
    "HR User",
    "HR Specialist",
    "Direct Manager",
]

EMPLOYEE_READ_ONLY_DOCTYPES = [
    "Loan Product",
    "Department",
    "Holiday List",
    "Project Type",
    "Project",
]

EMPLOYEE_FULL_DOCTYPES_LEVEL_0 = [
    "Task",
]


def create_custom_doc_perms():
    create_employee_read_only_docperms()
    create_employee_full_level_0_docperms()
    create_employee_read_level_1_docperms()
    create_manager_full_level_1_docperms()


def create_employee_read_only_docperms():
    for doctype in EMPLOYEE_READ_ONLY_DOCTYPES:
        for role in EMPLOYEE_ROLES:
            role = frappe.db.exists("Role", {"name": role})
            if not role:
                continue
            exists = frappe.db.exists(
                "Custom DocPerm", {"role": role, "parent": doctype, "permlevel": 0}
            )
            if exists:
                doc_perm = frappe.get_doc("Custom DocPerm", exists)
            else:
                doc_perm = frappe.new_doc("Custom DocPerm")
                doc_perm.update(
                    {
                        "role": role,
                        "parent": doctype,
                        "permlevel": 0,
                    }
                )
            doc_perm.update(
                {
                    "select": 1,
                    "read": 1,
                    "write": 0,
                    "create": 0,
                    "submit": 0,
                    "cancel": 0,
                    "amend": 0,
                    "report": 1,
                    "export": 1,
                    "import": 0,
                    "share": 1,
                    "print": 1,
                    "email": 1,
                }
            )
            doc_perm.save(ignore_permissions=True)


def create_employee_full_level_0_docperms():
    for doctype in EMPLOYEE_FULL_DOCTYPES_LEVEL_0:
        for role in EMPLOYEE_ROLES + MANAGER_ROLES:
            role = frappe.db.exists("Role", {"name": role})
            if not role:
                continue
            exists = frappe.db.exists(
                "Custom DocPerm", {"role": role, "parent": doctype, "permlevel": 0}
            )
            if exists:
                doc_perm = frappe.get_doc("Custom DocPerm", exists)
            else:
                doc_perm = frappe.new_doc("Custom DocPerm")
                doc_perm.update(
                    {
                        "role": role,
                        "parent": doctype,
                        "permlevel": 0,
                    }
                )
            doc_perm.update(
                {
                    "select": 1,
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": role in MANAGER_ROLES,
                    "submit": 0,
                    "cancel": 0,
                    "amend": 0,
                    "report": 1,
                    "export": 1,
                    "import": 0,
                    "share": 1,
                    "print": 1,
                    "email": 1,
                }
            )
            doc_perm.save(ignore_permissions=True)


def create_employee_read_level_1_docperms():
    for doctype in EMPLOYEE_FULL_DOCTYPES_LEVEL_0:
        for role in EMPLOYEE_ROLES:
            role = frappe.db.exists("Role", {"name": role})
            if not role:
                continue
            exists = frappe.db.exists(
                "Custom DocPerm", {"role": role, "parent": doctype, "permlevel": 1}
            )
            if exists:
                doc_perm = frappe.get_doc("Custom DocPerm", exists)
            else:
                doc_perm = frappe.new_doc("Custom DocPerm")
                doc_perm.update(
                    {
                        "role": role,
                        "parent": doctype,
                        "permlevel": 1,
                    }
                )
            doc_perm.update(
                {
                    "read": 1,
                    "write": 0,
                }
            )
            doc_perm.save(ignore_permissions=True)


def create_manager_full_level_1_docperms():
    for doctype in EMPLOYEE_FULL_DOCTYPES_LEVEL_0:
        for role in MANAGER_ROLES:
            role = frappe.db.exists("Role", {"name": role})
            if not role:
                continue
            exists = frappe.db.exists(
                "Custom DocPerm", {"role": role, "parent": doctype, "permlevel": 1}
            )
            if exists:
                doc_perm = frappe.get_doc("Custom DocPerm", exists)
            else:
                doc_perm = frappe.new_doc("Custom DocPerm")
                doc_perm.update(
                    {
                        "role": role,
                        "parent": doctype,
                        "permlevel": 1,
                    }
                )
            doc_perm.update(
                {
                    "read": 1,
                    "write": 1,
                }
            )
            doc_perm.save(ignore_permissions=True)
