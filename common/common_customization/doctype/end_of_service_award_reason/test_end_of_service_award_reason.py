# Copyright (c) 2026, Ahmed Madi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


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
