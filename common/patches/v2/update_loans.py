import frappe


def execute():
    loans = frappe.get_all(
        "Loan Application",
        filters={"applicant_type": "Employee"},
        fields=["name", "applicant"],
    )
    for loan in loans:
        frappe.db.set_value(
            "Loan Application",
            loan.name,
            "employee",
            loan.applicant,
            update_modified=False,
        )
    frappe.db.commit()
