# Copyright (c) 2026, Ahmed Madi and contributors
# For license information, please see license.txt

"""The end of service reasons shipped with the app.

These implement the Saudi Labour Law. They are seeded rather than hardcoded, so
a site can edit a formula, add a reason for another country, or scope one to a
single company without touching the code. Nothing here is overwritten once a
site has it - a reason is inserted only when it is missing.
"""

import frappe

# Article 84: half a month's wage for each of the first five years, a full
# month's wage for each year after that, pro rata for part of a year. Every
# other article is expressed as a share of this.
ART_84_AWARD = (
    "(0.5 * salary * 5 + salary * (years - 5)) if years > 5 else (0.5 * salary * years)"
)

REASONS = [
    {
        "title": (
            "Expiration the contract, agreement between the parties to terminate"
            " the contract, or termination the contract by the company"
        ),
        # Article 84, in the form it was originally written in the controller.
        "formula": (
            "(5 * salary * 0.5 + (years - 5) * salary)"
            " if years > 5"
            " else (years * salary * 0.5)"
        ),
        "exclude_award_from_total": 0,
    },
    {
        "title": "Employee resignation before the end of the contract period",
        # Article 85: nothing under two years, then a third of the Article 84
        # award up to five years, two thirds up to ten, and the whole of it at
        # ten years or more.
        "formula": (
            "0"
            " if years < 2"
            " else ((1 / 6) * salary * years"
            " if years <= 5"
            " else ((1 / 3) * salary * 5 + (2 / 3) * salary * (years - 5)"
            " if years < 10"
            " else 0.5 * salary * 5 + salary * (years - 5)))"
        ),
        "exclude_award_from_total": 0,
    },
    {
        "title": "End of the contract during the probation period",
        "formula": ART_84_AWARD,
        # No award is due during the probation period, but it is still
        # calculated and shown on the form.
        "exclude_award_from_total": 1,
    },
    {
        "title": "Termination of the contract by the employer for an unlawful reason",
        # Article 77 also entitles the employee to compensation on top of this
        # award. That is not part of the award itself - add it as an earning.
        "formula": ART_84_AWARD,
        "exclude_award_from_total": 0,
    },
    {
        "title": "Employee leaving the work for a force majeure beyond their control",
        # Article 87: the full award, whatever the length of service.
        "formula": ART_84_AWARD,
        "exclude_award_from_total": 0,
    },
    {
        "title": (
            "Female employee resigning within six months of marriage or three"
            " months of giving birth"
        ),
        # Article 87: the full award, whatever the length of service.
        "formula": ART_84_AWARD,
        "exclude_award_from_total": 0,
    },
    {
        "title": "Employee leaving the work due to a fault by the employer",
        # Article 81. The separate compensation it entitles the employee to is
        # not part of the award - add it as an earning.
        "formula": ART_84_AWARD,
        "exclude_award_from_total": 0,
    },
    {
        "title": "Termination of the contract by the employer for a cause under Article 80",
        # Article 80: no award at all.
        "formula": "0",
        "exclude_award_from_total": 0,
    },
]


def sync_reasons():
    """Insert the reasons a site does not have yet.

    Only ever inserts. A formula a site has edited is its own, and re-running
    this must not undo that.
    """
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
