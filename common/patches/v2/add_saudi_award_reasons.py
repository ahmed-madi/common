import frappe

from common.common_customization.doctype.end_of_service_award_reason.seed import (
    REASONS,
    sync_reasons,
)

RESIGNATION_REASON = "Employee resignation before the end of the contract period"

# What the resignation formula was seeded with before the Article 85 boundary
# was corrected. Only a reason still carrying this exact text is rewritten, so a
# site that has tuned its own formula keeps it.
SUPERSEDED_RESIGNATION_FORMULA = (
    "0"
    " if years < 2"
    " else ((1 / 6) * salary * years"
    " if years <= 5"
    " else ((1 / 3) * salary * 5 + (2 / 3) * salary * (years - 5)"
    " if years <= 10"
    " else 0.5 * salary * 5 + salary * (years - 5)))"
)


def execute():
    """Seed the reasons added after the first release, and correct Article 85.

    At exactly ten years of service the resignation formula paid two thirds of
    the award. Article 85 gives the whole of it from ten years onwards - the two
    thirds band stops short of ten.
    """
    sync_reasons()
    fix_resignation_boundary()


def fix_resignation_boundary():
    current = frappe.db.get_value(
        "End of Service Award Reason", RESIGNATION_REASON, "formula"
    )
    if current != SUPERSEDED_RESIGNATION_FORMULA:
        return

    corrected = next(r for r in REASONS if r["title"] == RESIGNATION_REASON)["formula"]
    frappe.db.set_value(
        "End of Service Award Reason", RESIGNATION_REASON, "formula", corrected
    )
