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
    "Sector Manager",
    "Department Manager",
    "Branch Manager",
]

EMPLOYEE_READ_ONLY_DOCTYPES = [
    "Loan Product",
    "Department",
    "Holiday List",
    "Project Type",
    "Project",
]

EMPLOYEE_FULL_DOCTYPES_LEVEL = [
    "Task",
]


def create_custom_doc_perms():
    ensure_roles_exist(EMPLOYEE_ROLES + MANAGER_ROLES)
    create_employee_doc_perms()
    create_manager_doc_perms()


def ensure_roles_exist(roles):
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role}).insert(
                ignore_if_duplicate=True
            )
    frappe.db.commit()


def create_employee_doc_perms():
    # Read-only doctypes
    for doctype in EMPLOYEE_READ_ONLY_DOCTYPES:
        for role in EMPLOYEE_ROLES:
            set_perms(role, doctype, read_only=True)

    # Full access except delete (e.g. Task)
    for doctype in EMPLOYEE_FULL_DOCTYPES_LEVEL:
        for role in EMPLOYEE_ROLES:
            set_perms(role, doctype, read_only=False, delete=0)


def create_manager_doc_perms():
    all_doctypes = EMPLOYEE_READ_ONLY_DOCTYPES + EMPLOYEE_FULL_DOCTYPES_LEVEL
    for doctype in all_doctypes:
        for role in MANAGER_ROLES:
            set_perms(role, doctype, read_only=False, delete=1)


def set_perms(role, doctype, read_only=False, delete=0):
    exists = frappe.db.exists(
        "Custom DocPerm", {"role": role, "parent": doctype, "permlevel": 0}
    )
    if exists:
        doc_perm = frappe.get_doc("Custom DocPerm", exists)
    else:
        doc_perm = frappe.new_doc("Custom DocPerm")
        doc_perm.update({"role": role, "parent": doctype, "permlevel": 0})

    doc_perm.update(
        {
            "select": 1,
            "read": 1,
            "write": 0 if read_only else 1,
            "create": 0 if read_only else 1,
            "delete": 0 if read_only else delete,
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
