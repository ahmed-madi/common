import frappe

# The reasons that used to be hardcoded Select options on End of Service Award,
# with the formulas transcribed from the old get_award(). The names are the
# exact option strings, so awards already saved against them keep resolving and
# the existing Arabic translations still match.
REASONS = [
    {
        "title": (
            "Expiration the contract, agreement between the parties to terminate"
            " the contract, or termination the contract by the company"
        ),
        "formula": (
            "(5 * salary * 0.5 + (years - 5) * salary)"
            " if years > 5"
            " else (years * salary * 0.5)"
        ),
        "exclude_award_from_total": 0,
    },
    {
        "title": "Employee resignation before the end of the contract period",
        "formula": (
            "0"
            " if years < 2"
            " else ((1 / 6) * salary * years"
            " if years <= 5"
            " else ((1 / 3) * salary * 5 + (2 / 3) * salary * (years - 5)"
            " if years <= 10"
            " else 0.5 * salary * 5 + salary * (years - 5)))"
        ),
        "exclude_award_from_total": 0,
    },
    {
        "title": "End of the contract during the probation period",
        "formula": (
            "(0.5 * salary * 5 + salary * (years - 5))"
            " if years > 5"
            " else (0.5 * salary * years)"
        ),
        # No end of service award is due during the probation period, but it is
        # still calculated and shown on the form.
        "exclude_award_from_total": 1,
    },
    {
        "title": "Termination of the contract by the employer for an unlawful reason",
        "formula": (
            "(0.5 * salary * 5 + salary * (years - 5))"
            " if years > 5"
            " else (0.5 * salary * years)"
        ),
        "exclude_award_from_total": 0,
    },
]


def execute():
    for reason in REASONS:
        if frappe.db.exists("End of Service Award Reason", reason["title"]):
            continue

        frappe.get_doc(
            {
                "doctype": "End of Service Award Reason",
                "amount_based_on_formula": 1,
                **reason,
            }
        ).insert(ignore_permissions=True)
