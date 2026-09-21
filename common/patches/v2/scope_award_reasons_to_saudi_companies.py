import frappe

from common.common_customization.doctype.end_of_service_award_reason.seed import (
    REASONS,
    get_saudi_companies,
    scoped_title,
    sync_saudi_reasons,
)


def execute():
    """Give every Saudi company its own end of service reasons.

    The reasons used to be seeded once, with no company, and shared by
    everybody. That only works while a site runs in one country.
    """
    adopt_shared_reasons()
    sync_saudi_reasons()


def adopt_shared_reasons():
    """Hand the existing shared reasons to the one company they can belong to.

    With a single Saudi company there is no ambiguity, so the reasons are
    renamed into its set rather than left beside a duplicate of themselves.
    Renaming carries the awards that point at them, including submitted ones.

    With none, or more than one, there is no safe answer, so they are left
    alone - a reason with no company still suits every company, so nothing
    breaks. Each Saudi company then gets its own set beside them, and an
    administrator can retire the shared ones.
    """
    companies = get_saudi_companies()
    if len(companies) != 1:
        return

    company = companies[0]

    for reason in REASONS:
        title = reason["title"]
        if not frappe.db.exists("End of Service Award Reason", title):
            continue

        # Only a reason nobody has claimed yet. One already scoped to a company
        # is somebody's deliberate choice.
        if frappe.db.get_value("End of Service Award Reason", title, "company"):
            continue

        new_title = scoped_title(title, company.abbr)
        if frappe.db.exists("End of Service Award Reason", new_title):
            continue

        frappe.rename_doc(
            "End of Service Award Reason",
            title,
            new_title,
            force=True,
            ignore_permissions=True,
            show_alert=False,
        )
        # The name is the title, so the field has to follow the rename.
        frappe.db.set_value(
            "End of Service Award Reason",
            new_title,
            {"title": new_title, "company": company.name},
            update_modified=False,
        )
