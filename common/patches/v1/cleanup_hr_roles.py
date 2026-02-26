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

EMPLOYEE_FULL_DOCTYPES_LEVEL = [
    "Task",
]


def execute():
    roles = EMPLOYEE_ROLES + MANAGER_ROLES
    doctypes = EMPLOYEE_READ_ONLY_DOCTYPES + EMPLOYEE_FULL_DOCTYPES_LEVEL

    frappe.db.delete(
        "Custom DocPerm", {"role": ["in", roles], "parent": ["in", doctypes]}
    )
    frappe.db.commit()
