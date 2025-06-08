import frappe
from frappe import _
from frappe.utils import flt

from lending.loan_management.doctype.loan_application.loan_application import (
    LoanApplication as BaseLoanApplication,
)


class LoanApplication(BaseLoanApplication):
    def validate(self):
        if hasattr(super(), "validate"):
            super().validate()
        self.validate_loan_policy()

    def validate_loan_policy(self):
        if self.applicant_type != "Employee":
            return

        filters = {}
        employee = frappe.db.get_value(
            "Employee", self.applicant, ["designation", "grade"], as_dict=True
        )
        designation = employee.get("designation")
        grade = employee.get("grade")
        if designation and designation is not None:
            filters.update(
                {
                    "policy_based_on": "Designation",
                    "criteria": designation,
                }
            )
        if grade and grade is not None:
            filters.update(
                {
                    "policy_based_on": "Employee Grade",
                    "criteria": grade,
                }
            )
        if not filters:
            return

        policies = frappe.get_all(
            "Employee Loan Policy",
            filters=filters,
            fields=["idx", "policy_based_on", "criteria", "limits_type", "loan_limits"],
            order_by="idx",
        )
        if len(policies) == 0:
            return
        policy = policies[0]
        if policy.limits_type == "Fixed Amount":
            if self.loan_amount > flt(policy.loan_limits):
                frappe.throw(
                    _(
                        "The loan amount exceeds the maximum allowable limit of {}."
                    ).format(policy.loan_limits)
                )
        elif policy.limits_type == "Percentage":
            loan_limits = flt(policy.loan_limits)
            gross_pay = self.get_last_gross_pay_salary_slip()
            if self.loan_amount > loan_limits * gross_pay / 100:
                frappe.throw(
                    _(
                        "The loan amount exceeds the maximum allowable limit of {}% of salary."
                    ).format(policy.loan_limits)
                )

    def get_last_gross_pay_salary_slip(self):
        if self.applicant_type != "Employee":
            return 0
        salary_slip = frappe.db.get_value(
            "Salary Slip",
            {"employee": self.applicant, "docstatus": 1},
            order_by="start_date desc",
        )
        if not salary_slip:
            frappe.throw(_("Employee does not have any salary slip"))
        return frappe.db.get_value("Salary Slip", salary_slip, "gross_pay")
