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


# The reasons above implement this country's law, so they are only seeded for a
# company that operates under it.
SAUDI_ARABIA = "Saudi Arabia"

# A reason is named after its title, and frappe names are varchar(140). The
# company suffix has to fit, so a long title gives way to it rather than the
# insert failing.
MAX_NAME_LENGTH = 140


def scoped_title(title, abbr):
    """A reason's title for one company, e.g. 'Employee resignation... - KSA'."""
    suffix = f" - {abbr}"
    return title[: MAX_NAME_LENGTH - len(suffix)] + suffix


def get_saudi_companies():
    # Company belongs to erpnext, which this app does not declare as required.
    # Seeding runs at install time, where a missing table would fail the whole
    # install rather than just skip the reasons.
    if not frappe.db.table_exists("Company"):
        return []

    return frappe.get_all(
        "Company", filters={"country": SAUDI_ARABIA}, fields=["name", "abbr"]
    )


def sync_reasons_for_company(company, abbr=None):
    """Give one company its own copy of the reasons.

    Each company carries its own set rather than sharing one, so a site can
    change a formula for a company without changing it everywhere - and a
    company in another country is never offered rules that do not apply to it.
    """
    abbr = abbr or frappe.db.get_value("Company", company, "abbr") or company

    for reason in REASONS:
        title = scoped_title(reason["title"], abbr)
        if frappe.db.exists("End of Service Award Reason", title):
            continue

        frappe.get_doc(
            {
                "doctype": "End of Service Award Reason",
                "amount_based_on_formula": 1,
                **reason,
                "title": title,
                "company": company,
            }
        ).insert(ignore_permissions=True)


def sync_saudi_reasons():
    """Seed every company that operates under the Saudi Labour Law.

    Called on install and whenever a company turns out to be Saudi, because a
    fresh site has no company yet when the app is installed - the setup wizard
    creates one afterwards.
    """
    for company in get_saudi_companies():
        sync_reasons_for_company(company.name, company.abbr)
