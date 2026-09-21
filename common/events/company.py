from common.common_customization.doctype.end_of_service_award_reason.seed import (
    SAUDI_ARABIA,
    sync_reasons_for_company,
)


def after_insert(doc, method=None):
    seed_award_reasons(doc)


def on_update(doc, method=None):
    # A company can be created under one country and corrected to another, and
    # only then become one the Saudi reasons apply to.
    if doc.has_value_changed("country"):
        seed_award_reasons(doc)


def seed_award_reasons(doc):
    """Give a Saudi company the end of service reasons its law calls for.

    A fresh site has no company when the app is installed - the setup wizard
    creates one afterwards - so install alone would never seed anything.
    """
    if doc.country != SAUDI_ARABIA:
        return

    sync_reasons_for_company(doc.name, doc.abbr)
