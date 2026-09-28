# Copyright (c) 2025, Ahmed Madi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from common.common_customization.doctype.end_of_service_award.end_of_service_award import (
    FORM_CALCULATED_FLAG,
    FORMULA_VARIABLES,
    recalculate,
)
from common.common_customization.doctype.end_of_service_award_reason.seed import (
    REASONS,
)


def seeded_copy(title):
    """The name of this test's own copy of a seeded reason.

    A site keeps its seeded reasons per company and may have edited their
    formulas, so the tests insert their own copies rather than lean on those.
    """
    return f"_Test {title}"[:140]


CONTRACT_END_REASON = seeded_copy(
    "Expiration the contract, agreement between the parties to terminate the contract,"
    " or termination the contract by the company"
)
RESIGNATION_REASON = seeded_copy(
    "Employee resignation before the end of the contract period"
)
PROBATION_REASON = seeded_copy("End of the contract during the probation period")
UNLAWFUL_REASON = seeded_copy(
    "Termination of the contract by the employer for an unlawful reason"
)


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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for reason in REASONS:
            name = seeded_copy(reason["title"])
            if frappe.db.exists("End of Service Award Reason", name):
                frappe.delete_doc("End of Service Award Reason", name, force=True)

            frappe.get_doc(
                {
                    "doctype": "End of Service Award Reason",
                    "amount_based_on_formula": 1,
                    **reason,
                    "title": name,
                    "company": None,
                }
            ).insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        for reason in REASONS:
            frappe.delete_doc(
                "End of Service Award Reason", seeded_copy(reason["title"]), force=True
            )
        super().tearDownClass()

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

    def test_resignation_at_exactly_ten_years_is_two_thirds(self):
        """The Select-era rule: the two thirds band runs up to and including ten."""
        award = make_award(RESIGNATION_REASON, salary=6000, years=10)
        award.get_award()

        # (1/3) * 6000 * 5 + (2/3) * 6000 * 5
        self.assertEqual(award.award, 30000)

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

    def make_reason(self, title, **kwargs):
        reason = frappe.get_doc(
            {
                "doctype": "End of Service Award Reason",
                "title": title,
                "amount_based_on_formula": 1,
                **kwargs,
            }
        ).insert()
        self.addCleanup(reason.delete)

        return reason

    def test_a_met_condition_lets_the_formula_run(self):
        reason = self.make_reason(
            "_Test Condition Met", condition="years >= 2", formula="salary * years"
        )

        award = make_award(reason.name, salary=6000, years=4)
        award.get_award()

        self.assertEqual(award.award, 24000)

    def test_an_unmet_condition_pays_nothing(self):
        reason = self.make_reason(
            "_Test Condition Unmet", condition="years >= 2", formula="salary * years"
        )

        award = make_award(reason.name, salary=6000, years=1, months=11)
        award.get_award()

        self.assertEqual(award.award, 0)

    def test_an_unmet_condition_skips_the_formula_entirely(self):
        """The formula may assume the condition holds, so it must not run when
        it does not - here it would raise ZeroDivisionError if it did."""
        reason = self.make_reason(
            "_Test Condition Guards Formula",
            condition="years >= 2",
            formula="salary / (years - 2)",
        )

        award = make_award(reason.name, salary=6000, years=0)
        award.get_award()

        self.assertEqual(award.award, 0)

    def test_no_condition_means_the_formula_always_runs(self):
        reason = self.make_reason("_Test No Condition", formula="salary * 2")

        award = make_award(reason.name, salary=6000, years=0)
        award.get_award()

        self.assertEqual(award.award, 12000)

    def test_a_condition_may_read_any_award_field(self):
        reason = self.make_reason(
            "_Test Condition On Doc",
            condition="doc.salary_is_already_taken == 0",
            formula="salary",
        )

        award = make_award(reason.name, salary=6000, years=4)
        award.salary_is_already_taken = 1
        award.get_award()

        self.assertEqual(award.award, 0)

    def test_a_broken_condition_says_it_was_the_condition(self):
        reason = self.make_reason(
            "_Test Broken Condition", condition="yeers >= 2", formula="salary"
        )

        award = make_award(reason.name, salary=6000, years=4)
        with self.assertRaises(frappe.ValidationError) as caught:
            award.get_award()

        message = str(caught.exception)
        self.assertIn(reason.name, message)
        self.assertIn("condition", message)

    def test_a_reason_without_a_company_suits_any_company(self):
        reason = self.make_reason("_Test Shared Reason", formula="salary")

        award = make_award(reason.name)
        award.company = "_Test Company"
        award.validate_reason_company()

    def test_a_reason_may_not_be_used_by_another_company(self):
        reason = self.make_reason(
            "_Test Scoped Reason", formula="salary", company="_Test Company"
        )

        award = make_award(reason.name)
        award.company = "_Test Company 1"
        with self.assertRaises(frappe.ValidationError) as caught:
            award.validate_reason_company()

        self.assertIn(reason.name, str(caught.exception))

    def test_a_reason_may_be_used_by_its_own_company(self):
        reason = self.make_reason(
            "_Test Own Company Reason", formula="salary", company="_Test Company"
        )

        award = make_award(reason.name)
        award.company = "_Test Company"
        award.validate_reason_company()

    def make_dated_award(self, days_number=0):
        award = make_award(None)
        award.update(
            {
                "work_start_date": "2020-01-01",
                "end_date": "2026-03-17",
                "days_number": days_number,
            }
        )
        return award

    def test_an_empty_days_number_is_filled_from_the_end_date(self):
        award = self.make_dated_award()
        award.calculate()

        self.assertEqual(award.days_number, 17)

    def test_a_days_number_entered_on_a_new_award_survives_the_first_save(self):
        award = self.make_dated_award(days_number=5)
        award.calculate()

        self.assertEqual(award.days_number, 5)

    def test_a_refetch_refills_an_entered_days_number(self):
        award = self.make_dated_award(days_number=5)
        award.calculate(refetch=True)

        self.assertEqual(award.days_number, 17)

    def test_calculate_derives_the_service_duration_and_totals(self):
        award = self.make_dated_award()
        award.ticket_number = 2
        award.ticket_cost = 1500
        award.calculate()

        self.assertEqual((award.years, award.months, award.days), (6, 2, 17))
        self.assertEqual(award.ticket_total_cost, 3000)
        self.assertEqual(award.total, 3000)

    def test_the_form_drops_a_reason_from_another_company(self):
        company = frappe.get_all("Company", pluck="name", limit=1)[0]
        reason = self.make_reason(
            "_Test Form Scoped Reason", formula="salary", company=company
        )

        award = make_award(reason.name)
        award.company = f"{company} - elsewhere"
        values = recalculate(award.as_json())["values"]

        self.assertIsNone(values["reason"])
        self.assertEqual(values["award"], 0)

    def test_the_form_gets_the_award_from_the_reason(self):
        award = make_award(CONTRACT_END_REASON, salary=6000, years=3)
        award.update({"work_start_date": "2023-01-01", "end_date": "2025-12-30"})
        values = recalculate(award.as_json())["values"]

        # 3 * 6000 * 0.5, with the duration worked out from the dates
        self.assertEqual((values["years"], values["months"], values["days"]), (3, 0, 0))
        self.assertEqual(values["award"], 9000)
        self.assertEqual(values["total"], 9000)

    def make_saved_award_with_new_end_date(self, days_number):
        """A draft whose end date was changed since it was saved."""
        award = self.make_dated_award(days_number=days_number)
        before = frappe.copy_doc(award)
        before.end_date = "2026-02-10"
        award._doc_before_save = before

        return award

    def test_a_save_from_the_form_keeps_what_the_form_decided(self):
        """The form refilled on the date change and the user typed over it
        afterwards - the save must not refill it a second time."""
        award = self.make_saved_award_with_new_end_date(days_number=5)
        award.set(FORM_CALCULATED_FLAG, 1)
        award.validate()

        self.assertEqual(award.days_number, 5)

    def test_a_save_from_elsewhere_refills_after_a_date_change(self):
        award = self.make_saved_award_with_new_end_date(days_number=5)
        award.validate()

        self.assertEqual(award.days_number, 17)

    def test_the_form_is_told_about_a_missing_salary_slip_instead_of_failing(self):
        slipless = frappe.get_all(
            "Employee",
            filters={
                "name": [
                    "not in",
                    frappe.get_all(
                        "Salary Slip", filters={"docstatus": 1}, pluck="employee"
                    )
                    or [""],
                ]
            },
            pluck="name",
            limit=1,
        )
        if not slipless:
            self.skipTest("Every employee on this site has a salary slip")

        award = make_award(None, salary=0)
        award.employee = slipless[0]
        result = recalculate(award.as_json())

        self.assertTrue(result["missing_salary_slip"])
        self.assertEqual(result["values"]["salary"], 0)

        # The save still refuses it.
        self.assertRaises(frappe.ValidationError, award.calculate_salary_details)
