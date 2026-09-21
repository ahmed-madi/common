# Copyright (c) 2026, Ahmed Madi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from common import employee_snapshot

COMPANY = "_Test Company"


class TestEmployeeSnapshot(FrappeTestCase):
    def tearDown(self):
        frappe.db.rollback()
        frappe.clear_document_cache("Company Policy", COMPANY)

    def get_policy(self):
        """This company's policy, created if the site has none for it.

        Company Policy is per company now, so a test has to say which.
        """
        if frappe.db.exists("Company Policy", COMPANY):
            return frappe.get_doc("Company Policy", COMPANY)

        policy = frappe.new_doc("Company Policy")
        policy.company = COMPANY
        policy.flags.ignore_mandatory = True
        policy.flags.ignore_validate = True

        return policy.insert(ignore_permissions=True)

    def set_categories(self, mapping):
        policy = self.get_policy()
        policy.salary_component_categories = []
        for component, category in mapping.items():
            policy.append(
                "salary_component_categories",
                {"salary_component": component, "type": category},
            )
        policy.flags.ignore_mandatory = True
        policy.flags.ignore_validate = True
        policy.save(ignore_permissions=True)
        frappe.clear_document_cache("Company Policy", COMPANY)

    def test_components_total_into_their_configured_category(self):
        self.set_categories(
            {
                "_Test Basic": "Basic",
                "_Test Housing": "Housing Allowance",
                "_Test Transport": "Transportation Allowance",
            }
        )

        totals = employee_snapshot.classify(
            {"_Test Basic": 10000, "_Test Housing": 2500, "_Test Transport": 800},
            COMPANY,
        )

        self.assertEqual(totals["custom_basic_salary"], 10000)
        self.assertEqual(totals["custom_housing_allowance"], 2500)
        self.assertEqual(totals["custom_transportation_allowance"], 800)
        self.assertEqual(totals["custom_other_allowances"], 0)

    def test_an_unclassified_component_is_an_other_allowance(self):
        """Nothing may be dropped - an employee's parts must add up to the
        whole, even when nobody has categorised a component."""
        self.set_categories({"_Test Basic": "Basic"})

        totals = employee_snapshot.classify(
            {"_Test Basic": 10000, "_Test Mystery": 400}, COMPANY
        )

        self.assertEqual(totals["custom_basic_salary"], 10000)
        self.assertEqual(totals["custom_other_allowances"], 400)

    def test_a_category_this_app_no_longer_knows_is_an_other_allowance(self):
        """Travel Allowance was dropped as a category. Rows a site already had
        must fall into other allowances rather than vanish."""
        self.set_categories({"_Test Travel": "Travel Allowance"})

        totals = employee_snapshot.classify({"_Test Travel": 600}, COMPANY)

        self.assertEqual(totals["custom_other_allowances"], 600)

    def test_two_components_in_one_category_are_added_together(self):
        self.set_categories(
            {"_Test Housing A": "Housing Allowance", "_Test Housing B": "Housing Allowance"}
        )

        totals = employee_snapshot.classify(
            {"_Test Housing A": 1500, "_Test Housing B": 700}, COMPANY
        )

        self.assertEqual(totals["custom_housing_allowance"], 2200)

    def test_no_salary_slip_means_zeroes_not_an_error(self):
        totals = employee_snapshot.get_salary_snapshot("_Test Employee Without Slips")

        self.assertEqual(set(totals), set(employee_snapshot.SNAPSHOT_FIELDS))
        self.assertTrue(all(value == 0 for value in totals.values()))

    def test_no_annual_leave_type_configured_gives_none_not_zero(self):
        """A missing setting is not a zero balance, and writing zero would read
        as one."""
        self.get_policy()
        frappe.db.set_value("Company Policy", COMPANY, "annual_leave_type", None)
        frappe.clear_document_cache("Company Policy", COMPANY)

        employee = frappe.db.get_value("Employee", {"company": COMPANY}, "name")
        if not employee:
            self.skipTest(f"no employee in {COMPANY}")

        self.assertIsNone(employee_snapshot.get_annual_leave_balance(employee))

    def test_updating_an_unknown_employee_does_nothing(self):
        employee_snapshot.update_employee("_Test Nonexistent Employee")
