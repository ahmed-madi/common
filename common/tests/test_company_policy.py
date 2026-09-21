# Copyright (c) 2026, Ahmed Madi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from common import company_policy

COMPANY = "_Test Company"


class TestCompanyPolicy(FrappeTestCase):
    def tearDown(self):
        frappe.db.rollback()
        frappe.clear_document_cache("Company Policy", COMPANY)

    def make_policy(self, company, **values):
        if frappe.db.exists("Company Policy", company):
            policy = frappe.get_doc("Company Policy", company)
        else:
            policy = frappe.new_doc("Company Policy")
            policy.company = company

        policy.update(values)
        policy.flags.ignore_mandatory = True
        policy.flags.ignore_validate = True

        return policy.save(ignore_permissions=True)

    def test_a_company_gets_its_own_policy(self):
        self.make_policy(COMPANY, max_wfh_days=3)

        self.assertEqual(company_policy.get_policy_name(COMPANY), COMPANY)
        self.assertEqual(company_policy.get_policy_value("max_wfh_days", COMPANY), 3)

    def test_two_companies_keep_separate_settings(self):
        """The whole point of the change: one company's rule is not another's."""
        other = "_Test Company 1"
        if not frappe.db.exists("Company", other):
            self.skipTest(f"{other} does not exist on this site")

        self.make_policy(COMPANY, max_wfh_days=3)
        self.make_policy(other, max_wfh_days=10)

        self.assertEqual(company_policy.get_policy_value("max_wfh_days", COMPANY), 3)
        self.assertEqual(company_policy.get_policy_value("max_wfh_days", other), 10)

    def test_a_company_without_a_policy_says_so(self):
        """Silently falling back to another company's policy would apply the
        wrong rules, which is worse than refusing to answer."""
        company = "_Test Company With No Policy"
        frappe.db.delete("Company Policy", {"company": company})

        with self.assertRaises(frappe.ValidationError) as caught:
            company_policy.get_policy_name(company)

        self.assertIn(company, str(caught.exception))

    def test_an_employee_resolves_to_their_company_policy(self):
        employee = frappe.db.get_value("Employee", {"company": COMPANY}, "name")
        if not employee:
            self.skipTest(f"no employee in {COMPANY}")

        self.make_policy(COMPANY, max_wfh_days=7)

        self.assertEqual(company_policy.get_employee_policy(employee).name, COMPANY)
