import frappe

from common.common_customization.doctype.end_of_service_award_reason.seed import (
    REASONS,
    get_saudi_companies,
    scoped_title,
    sync_reasons_for_company,
)

REASON = "End of Service Award Reason"
AWARD = "End of Service Award"


def execute():
    """Keep only the four reasons the Select field offered, with its rules.

    Every Saudi company gets exactly those four, carrying the formulas the award
    was calculated with before the reason became a Link. Everything else is
    dropped. An award pointing at a dropped copy of one of the four is moved to
    its company's own copy first, so no award - submitted ones included - is
    left pointing at a reason that no longer exists.
    """
    companies = get_saudi_companies()
    abbr_by_company = {company.name: company.abbr for company in companies}

    kept = set()
    for company in companies:
        kept.update(reset_company_reasons(company.name, company.abbr))

    for name in frappe.get_all(REASON, pluck="name"):
        if name in kept:
            continue

        move_awards(name, abbr_by_company)
        drop_reason(name)


def reset_company_reasons(company, abbr):
    """The company's four reasons, created if missing and set to the seeded rules."""
    sync_reasons_for_company(company, abbr)

    names = []
    for reason in REASONS:
        name = scoped_title(reason["title"], abbr)
        doc = frappe.get_doc(REASON, name)
        doc.update(
            {
                "company": company,
                "amount_based_on_formula": 1,
                "amount": 0,
                "condition": None,
                "formula": reason["formula"],
                "exclude_award_from_total": reason["exclude_award_from_total"],
            }
        )
        doc.save(ignore_permissions=True)
        names.append(name)

    return names


def get_seeded_title(name, abbrs):
    """Which of the four reasons `name` is a copy of, shared or scoped, if any."""
    for reason in REASONS:
        title = reason["title"]
        if name == title or any(name == scoped_title(title, abbr) for abbr in abbrs):
            return title

    return None


def move_awards(name, abbr_by_company):
    title = get_seeded_title(name, abbr_by_company.values())
    if not title:
        return

    awards = frappe.get_all(AWARD, filters={"reason": name}, fields=["name", "company"])
    for award in awards:
        abbr = abbr_by_company.get(award.company)
        if not abbr:
            continue

        frappe.db.set_value(
            AWARD,
            award.name,
            "reason",
            scoped_title(title, abbr),
            update_modified=False,
        )


def drop_reason(name):
    """Delete the reason, unless an award still needs it.

    That is an award using a reason that is not one of the four, or one whose
    company has no set of its own. Its reason is kept rather than the award
    left pointing at nothing, and the log says so.
    """
    if frappe.db.exists(AWARD, {"reason": name}):
        print(f"Kept End of Service Award Reason {name!r}: still used by an award")
        return

    frappe.delete_doc(REASON, name, ignore_permissions=True, force=True)
