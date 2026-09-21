# Copyright (c) 2026, Ahmed Madi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from common.common_customization.doctype.end_of_service_award_reason import seed
from common.events import company


class TestEndofServiceAwardReason(FrappeTestCase):
    def test_condition_must_be_an_expression(self):
        reason = frappe.get_doc(
            {
                "doctype": "End of Service Award Reason",
                "title": "_Test Broken Condition Syntax",
                "amount_based_on_formula": 1,
                "condition": "years = 2",
                "formula": "salary",
            }
        )

        self.assertRaises(frappe.ValidationError, reason.insert)

    def test_condition_is_optional(self):
        reason = frappe.get_doc(
            {
                "doctype": "End of Service Award Reason",
                "title": "_Test No Condition Needed",
                "amount_based_on_formula": 1,
                "formula": "salary",
            }
        ).insert()
        self.addCleanup(reason.delete)

        self.assertFalse(reason.condition)

    def test_formula_must_be_an_expression(self):
        reason = frappe.get_doc(
            {
                "doctype": "End of Service Award Reason",
                "title": "_Test Broken Formula",
                "amount_based_on_formula": 1,
                "formula": "salary = 1",
            }
        )

        self.assertRaises(frappe.ValidationError, reason.insert)

    def test_fixed_amount_clears_the_formula(self):
        reason = frappe.get_doc(
            {
                "doctype": "End of Service Award Reason",
                "title": "_Test Fixed Amount",
                "amount_based_on_formula": 0,
                "amount": 1000,
                "condition": "years >= 2",
                "formula": "salary * 2",
            }
        ).insert()
        self.addCleanup(reason.delete)

        self.assertIsNone(reason.formula)
        self.assertIsNone(reason.condition)


class TestSeedAwardReasons(FrappeTestCase):
    def tearDown(self):
        frappe.db.rollback()

    def test_scoped_title_carries_the_company(self):
        self.assertEqual(
            seed.scoped_title("Employee resignation", "KSA"),
            "Employee resignation - KSA",
        )

    def test_a_long_title_gives_way_to_the_company_suffix(self):
        """The title is the name, and a name is varchar(140). A long title with
        a long abbreviation has to fit, rather than fail on insert."""
        title = "x" * 200
        scoped = seed.scoped_title(title, "SAUDIARABIA1234")

        self.assertEqual(len(scoped), seed.MAX_NAME_LENGTH)
        self.assertTrue(scoped.endswith(" - SAUDIARABIA1234"))

    def test_every_shipped_title_fits_with_a_normal_abbreviation(self):
        for reason in seed.REASONS:
            self.assertLessEqual(
                len(seed.scoped_title(reason["title"], "KSA")), seed.MAX_NAME_LENGTH
            )

    def test_seeding_gives_a_company_its_own_set(self):
        seed.sync_reasons_for_company("_Test Company", "_TC")

        for reason in seed.REASONS:
            title = seed.scoped_title(reason["title"], "_TC")
            self.assertEqual(
                frappe.db.get_value("End of Service Award Reason", title, "company"),
                "_Test Company",
            )

    def test_seeding_twice_does_not_duplicate_or_overwrite(self):
        seed.sync_reasons_for_company("_Test Company", "_TC")

        title = seed.scoped_title(seed.REASONS[0]["title"], "_TC")
        frappe.db.set_value("End of Service Award Reason", title, "formula", "salary")

        seed.sync_reasons_for_company("_Test Company", "_TC")

        self.assertEqual(
            frappe.db.count("End of Service Award Reason", {"company": "_Test Company"}),
            len(seed.REASONS),
        )
        # A site's own edit to a formula survives re-seeding.
        self.assertEqual(
            frappe.db.get_value("End of Service Award Reason", title, "formula"),
            "salary",
        )

    def test_only_a_saudi_company_is_seeded(self):
        company.seed_award_reasons(
            frappe._dict(name="_Test Company", abbr="_TC", country="United Kingdom")
        )

        self.assertEqual(
            frappe.db.count("End of Service Award Reason", {"company": "_Test Company"}),
            0,
        )

    def test_a_saudi_company_is_seeded(self):
        company.seed_award_reasons(
            frappe._dict(name="_Test Company", abbr="_TC", country=seed.SAUDI_ARABIA)
        )

        self.assertEqual(
            frappe.db.count("End of Service Award Reason", {"company": "_Test Company"}),
            len(seed.REASONS),
        )
