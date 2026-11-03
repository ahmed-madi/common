import frappe


def execute():
    """Make room for lending v16's standard `loan_purpose` field.

    Lending v16 ships Loan Application.loan_purpose as a Link to Loan Purpose,
    which clashes with this app's free-text custom field of the same name and
    makes the doctype fail validation on migrate. Runs before model sync: keep
    the free text in `remarks`, clear the column and drop the custom field.
    """
    custom_field = frappe.db.get_value(
        "Custom Field", {"dt": "Loan Application", "fieldname": "loan_purpose"}
    )
    if not custom_field:
        return

    columns = frappe.db.get_table_columns("Loan Application")
    if "loan_purpose" in columns:
        if "remarks" in columns:
            for row in frappe.db.sql(
                """select name, loan_purpose, remarks from `tabLoan Application`
                where ifnull(loan_purpose, '') != ''""",
                as_dict=True,
            ):
                remarks = "\n\n".join(filter(None, [row.loan_purpose, row.remarks]))
                frappe.db.set_value(
                    "Loan Application", row.name, "remarks", remarks, update_modified=False
                )

        frappe.db.sql("update `tabLoan Application` set loan_purpose = null")

    frappe.db.delete("Custom Field", {"name": custom_field})
    frappe.clear_cache(doctype="Loan Application")
