# Copyright (c) 2025, Ahmed Madi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from common.common_customization.doctype.end_of_service_award.end_of_service_award import (
    FORMULA_VARIABLES,
)

CONTRACT_END_REASON = (
    "Expiration the contract, agreement between the parties to terminate the contract,"
    " or termination the contract by the company"
)
RESIGNATION_REASON = "Employee resignation before the end of the contract period"
PROBATION_REASON = "End of the contract during the probation period"
UNLAWFUL_REASON = "Termination of the contract by the employer for an unlawful reason"


def make_award(reason, salary=6000, years=0, months=0, days=0):
    """An unsaved award carrying only what the award formulas read.

    Built with `frappe.new_doc` rather than inserted, so the formulas can be
    exercised without an employee, a salary structure or a salary slip.
    """
    award = frappe.new_doc("End of Service Award")
    award.update(
        {
            "reason": reason,
            "salary": salary,
            "years": years,
            "months": months,
            "days": days,
        }
    )

    return award


class TestEndofServiceAward(FrappeTestCase):
    """The seeded reasons must reproduce the numbers the hardcoded rules gave.

    Each expected value is the old get_award() branch worked out by hand, so a
    change to a seeded formula shows up here rather than on a payslip.
    """

    def test_contract_end_under_five_years(self):
        award = make_award(CONTRACT_END_REASON, salary=6000, years=3)
        award.get_award()

        # 3 * 6000 * 0.5
        self.assertEqual(award.award, 9000)

    def test_contract_end_over_five_years(self):
        award = make_award(CONTRACT_END_REASON, salary=6000, years=8)
        award.get_award()

        # 5 * 6000 * 0.5 + 3 * 6000
        self.assertEqual(award.award, 33000)

    def test_resignation_under_two_years_earns_nothing(self):
        award = make_award(RESIGNATION_REASON, salary=6000, years=1, months=11)
        award.get_award()

        self.assertEqual(award.award, 0)

    def test_resignation_between_two_and_five_years(self):
        award = make_award(RESIGNATION_REASON, salary=6000, years=4)
        award.get_award()

        # (1/6) * 6000 * 4
        self.assertEqual(award.award, 4000)

    def test_resignation_between_five_and_ten_years(self):
        award = make_award(RESIGNATION_REASON, salary=6000, years=8)
        award.get_award()

        # (1/3) * 6000 * 5 + (2/3) * 6000 * 3
        self.assertEqual(award.award, 22000)

    def test_resignation_over_ten_years(self):
        award = make_award(RESIGNATION_REASON, salary=6000, years=12)
        award.get_award()

        # 0.5 * 6000 * 5 + 6000 * 7
        self.assertEqual(award.award, 57000)

    def test_unlawful_termination_over_five_years(self):
        award = make_award(UNLAWFUL_REASON, salary=6000, years=8)
        award.get_award()

        # 0.5 * 6000 * 5 + 6000 * 3
        self.assertEqual(award.award, 33000)

    def test_months_and_days_count_as_part_of_a_year(self):
        award = make_award(CONTRACT_END_REASON, salary=6000, years=2, months=6, days=18)
        award.get_award()

        # (2 + 6/12 + 18/360) * 6000 * 0.5
        self.assertEqual(award.award, 7650)

    def test_probation_award_is_calculated_but_excluded_from_the_total(self):
        award = make_award(PROBATION_REASON, salary=6000, years=3)
        award.get_award()

        self.assertEqual(award.award, 9000)
        self.assertTrue(award.award_is_excluded())

        award.calculate_total_award()
        self.assertEqual(award.total, 0)

    def test_other_reasons_are_not_excluded_from_the_total(self):
        award = make_award(CONTRACT_END_REASON, salary=6000, years=3)
        award.get_award()

        self.assertFalse(award.award_is_excluded())

        award.calculate_total_award()
        self.assertEqual(award.total, 9000)

    def test_no_reason_means_no_award(self):
        award = make_award(None, salary=6000, years=8)
        award.get_award()

        self.assertEqual(award.award, 0)
        self.assertFalse(award.award_is_excluded())

    def test_a_reason_with_a_fixed_amount_pays_that_amount(self):
        reason = frappe.get_doc(
            {
                "doctype": "End of Service Award Reason",
                "title": "_Test Fixed Award",
                "amount_based_on_formula": 0,
                "amount": 7500,
            }
        ).insert()
        self.addCleanup(reason.delete)

        award = make_award(reason.name, salary=6000, years=8)
        award.get_award()

        self.assertEqual(award.award, 7500)

    def test_a_broken_formula_names_the_reason_it_came_from(self):
        reason = frappe.get_doc(
            {
                "doctype": "End of Service Award Reason",
                "title": "_Test Unknown Variable",
                "amount_based_on_formula": 1,
                "formula": "salery * 2",
            }
        ).insert()
        self.addCleanup(reason.delete)

        award = make_award(reason.name, salary=6000, years=8)
        with self.assertRaises(frappe.ValidationError) as caught:
            award.get_award()

        self.assertIn(reason.name, str(caught.exception))

    def test_documented_variables_are_the_ones_a_formula_gets(self):
        """The help on End of Service Award Reason is built from
        FORMULA_VARIABLES, so it is only honest while that matches the context
        the formula is actually evaluated against."""
        award = make_award(CONTRACT_END_REASON)

        self.assertEqual(set(FORMULA_VARIABLES), set(award.get_formula_context()))
