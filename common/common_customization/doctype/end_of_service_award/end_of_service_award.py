# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import math
from frappe.utils import (
    cint,
    date_diff,
    flt,
    getdate,
    get_link_to_form,
    nowdate,
    get_defaults,
    now_datetime,
)

from dateutil import relativedelta
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
)


class EndofServiceAward(Document):
    def validate(self):
        if self.end_date and self.work_start_date:
            years, months, days = self.get_days_months_years(
                self.end_date, self.work_start_date
            )
            self.years = years
            self.months = months
            self.days = days
            diffDays = date_diff(self.end_date, self.work_start_date) + 1
            if diffDays < 30:
                if not self.days_number:
                    self.days_number = diffDays
            else:
                if not self.days_number:
                    self.days_number = getdate(self.end_date).day

        if self.employee:
            (
                total_salary,
                total_day_value,
                basic,
                basic_day_value,
                housing_allowance,
                housing_day_value,
                transportation_allowance,
                transportation_day_value,
                other_allowance,
                other_day_value,
                salary_structure,
            ) = self.get_salary(self.employee)

            self.salary_structure = salary_structure
            self.salary = total_salary
            self.day_value = total_day_value  # total day value
            self.leave_cost = total_day_value
            self.basic = basic
            self.basic_day_value = basic_day_value
            self.total_month_basic = flt(self.days_number) * flt(self.basic_day_value)
            self.housing_allowance = housing_allowance
            self.housing_day_value = housing_day_value
            self.total_month_housing = flt(self.days_number) * flt(
                self.housing_day_value
            )
            self.transportation_allowance = transportation_allowance
            self.transportation_day_value = transportation_day_value
            self.total_month_transportation = flt(self.days_number) * flt(
                self.transportation_day_value
            )
            self.other_allowance = 0  # other_allowance -temporarily set as zero-
            self.other_day_value = other_day_value
            self.total_month_other = flt(self.days_number) * flt(self.other_day_value)

        if (
            self.employee
            and self.work_start_date
            and self.end_date
            and not self.leave_number
        ):
            self.leave_number = self.get_leave_balance(
                self.employee, self.work_start_date, self.end_date
            )

        self.total_month_salary = 0
        if cint(self.salary_is_already_taken) == 0:
            self.total_month_salary = flt(self.days_number) * flt(self.day_value)

        self.calculate_total_earning()
        self.calculate_total_deduction()

        if not self.leave_total_cost:
            self.leave_total_cost = flt(self.leave_number) * flt(self.leave_cost)

        self.get_award()
        self.calculate_total_award()

    def get_award(self):
        self.award = 0
        salary = flt(self.salary)
        years = cint(self.years) + cint(self.months) / 12 + cint(self.days) / 360

        if (
            self.reason
            == "Expiration the contract, agreement between the parties to terminate the contract, or termination the contract by the company"
        ):
            firstPeriod = secondPeriod = 0
            if years > 5:
                firstPeriod = 5
                secondPeriod = years - 5
            else:
                firstPeriod = years
            result = firstPeriod * salary * 0.5 + secondPeriod * salary
            self.award = round(result * 100) / 100
        elif self.reason == "Employee resignation before the end of the contract period":
            result = 0
            if years < 2:
                result = 0
            elif years <= 5:
                result = (1 / 6) * salary * years
            elif years <= 10:
                result = (1 / 3) * salary * 5 + (2 / 3) * salary * (years - 5)
            else:
                result = 0.5 * salary * 5 + salary * (years - 5)
            self.award = round(result * 100) / 100
        else:
            result = 0
            if years <= 5:
                result = 0.5 * salary * years
            else:
                result = 0.5 * salary * 5 + salary * (years - 5)
            self.award = round(result * 100) / 100

    def calculate_total_award(self):
        if self.reason == "End of the contract during the probation period":
            totals = (
                flt(self.ticket_total_cost)
                + flt(self.total_month_salary)
                + flt(self.leave_total_cost)
                + flt(self.total_earning)
            )
            self.total = (
                totals - flt(self.total_deduction)
                if totals >= flt(self.total_deduction)
                else 0
            )
        else:
            totals = (
                flt(self.award)
                + flt(self.ticket_total_cost)
                + flt(self.total_month_salary)
                + flt(self.leave_total_cost)
                + flt(self.total_earning)
            )
            self.total = (
                totals - flt(self.total_deduction)
                if totals >= flt(self.total_deduction)
                else 0
            )

    def calculate_total_deduction(self):
        self.total_deduction = 0
        if not self.end_of_service_award_deduction:
            return
        for row in self.end_of_service_award_deduction or []:
            self.total_deduction += flt(row.get("deduction", 0))

    def calculate_total_earning(self):
        self.total_earning = 0
        if not self.end_of_service_award_earning:
            return

        for row in self.end_of_service_award_earning or []:
            self.total_earning += flt(row.get("earning", 0))

    @frappe.whitelist()
    def get_salary(self, employee):
        total_salary = 0

        basic_salary = 0
        housing_allowance = 0
        transportation_allowance = 0
        other_allowances = 0

        salary_slips = frappe.get_list(
            "Salary Slip",
            fields=["name", "salary_structure"],
            filters={"employee": employee, "docstatus": 1},
            order_by="start_date desc",
        )
        if not salary_slips or len(salary_slips) == 0:
            frappe.throw(_("No salary found for this employee"))

        salary_slip = salary_slips[0].name
        salary_structure = salary_slips[0].salary_structure

        salary_details = frappe.db.sql(
            """
            SELECT salary_component, amount
            FROM `tabSalary Detail`
            WHERE parent='{0}' AND parentfield='earnings' AND parenttype='Salary Slip'
            """.format(
                salary_slip
            ),
            as_dict=True,
        )
        if not salary_details:
            frappe.throw(_("No salary found for this employee"))

        basic_components = []
        housing_components = []
        transportation_components = []
        for c in frappe.db.sql(
            "SELECT salary_component, parentfield from `tabCustom Salary Component`",
            as_dict=True,
        ):
            if c.parentfield == "custom_basic_components":
                basic_components.append(c.salary_component)
            elif c.parentfield == "custom_housing_allowance_components":
                housing_components.append(c.salary_component)
            elif c.parentfield == "custom_transportation_allowance_components":
                transportation_components.append(c.salary_component)
        for detail in salary_details:
            component = detail.get("salary_component")
            amount = flt(detail.get("amount", 0))

            if component in basic_components:
                basic_salary += amount
                total_salary += amount
            elif component in housing_components:
                housing_allowance += amount
                total_salary += amount
            elif component in transportation_components:
                transportation_allowance += amount
                total_salary += amount
            else:
                other_allowances += amount

            # total_salary += amount  # removed because they want the total salary be the sum of three main components

        return (
            total_salary,
            flt(total_salary / 30, 2),
            basic_salary,
            flt(basic_salary / 30, 2),
            housing_allowance,
            flt(housing_allowance / 30, 2),
            transportation_allowance,
            flt(transportation_allowance / 30, 2),
            other_allowances,
            flt(other_allowances / 30, 2),
            salary_structure,
        )

    @frappe.whitelist()
    def get_days_months_years(self, end_date, work_start_date):
        difference = relativedelta.relativedelta(
            getdate(end_date), getdate(work_start_date)
        )
        years = difference.years
        months = difference.months
        days = difference.days + 1

        if days >= 30:
            months += 1
            days -= 30

        if months >= 12:
            years += 1
            months -= 12

        return years, months, days

    @frappe.whitelist()
    def get_leave_balance(self, employee, work_start_date, end_date):
        today = now_datetime().date()
        end = end_date
        total_leave_balance = frappe.db.sql(
            """SELECT total_leaves_allocated, from_date, to_date,name
                FROM `tabLeave Allocation`
                WHERE employee='{0}' AND leave_type='Annual Leave' ORDER BY creation DESC LIMIT 1
                """.format(
                employee
            )
        )
        if total_leave_balance:
            leave_days = frappe.db.sql(
                """SELECT SUM(total_leave_days)
                FROM `tabLeave Application`
                WHERE employee='{0}' AND leave_type='Annual Leave' AND posting_date BETWEEN '{1}' AND '{2}'""".format(
                    employee, total_leave_balance[0][1], total_leave_balance[0][2]
                )
            )[0][0]
            if not leave_days:
                leave_days = 0.0

            leave_balance = total_leave_balance[0][0] - leave_days
            # Check if end date is greater than today
            if getdate(end) > getdate(today):
                diff_to_today = date_diff(today, end)
                additional_leave_balance = diff_to_today * -0.083
                leave_balance += additional_leave_balance

            # Check if end date is smaller than today
            elif getdate(end) < getdate(today):
                diff_to_today = date_diff(today, end)
                additional_leave_balance = diff_to_today * 0.083
                leave_balance -= additional_leave_balance

        else:
            leave_balance = 0.0

        if leave_balance < 0:
            leave_balance = 0

        return leave_balance

    @frappe.whitelist()
    def set_rejection_reason(self, rejection_reason):
        if self.workflow_state == "Waiting for Employee Review":
            self.db_set("rejection_reason", rejection_reason)
            return "Done"
        return "Error"

    def on_update(self):
        prev_doc = self.get_doc_before_save() or {}
        # is new or status not changed!
        if self.is_new() or self.workflow_state == prev_doc.get("workflow_state"):
            return

        user_id = frappe.db.get_value("Employee", self.employee, "user_id")
        if not user_id:
            return

        if self.workflow_state == "Waiting for Employee Review":
            # Send notification for employee to make review
            notification_doc = {
                "type": "Alert",
                "document_type": "End of Service Award",
                "document_name": self.name,
                "subject": "End of Service Award is waiting for you to review.",
                "from_user": "Administrator",
            }
            enqueue_create_notification([user_id], notification_doc)

        # TODO send notification for direct manager when reject end of service award
        # direct_manager = frappe.db.get_value("Employee", self.employee, 'reports_to')
        # if not direct_manager:
        #     return
        # direct_manager_user_id = frappe.db.get_value("Employee", direct_manager, 'user_id')
        # if not direct_manager_user_id:
        #     return
        # if self.workflow_state == "Rejected By Employee":
        #     # Send notification for employee to make review
        #     notification_doc = {
        #         "type": "Alert",
        #         "document_type": "End of Service Award",
        #         "document_name": self.name,
        #         "subject": "End of Service Award was Rejected by the employee.",
        #         "from_user": "Administrator",
        #     }
        #     enqueue_create_notification([direct_manager_user_id], notification_doc)

    @frappe.whitelist()
    def make_journal_entry(self):
        if self.docstatus != 1:
            frappe.throw(_("Can not create journal entry"))
        jvs = end_of_service_has_jv_entries(self.name, [0, 1])
        if jvs.get("submitted", 0) == 1:
            return jvs

        company = frappe.db.get_value("Employee", self.employee, "company")

        if not company:
            frappe.throw(_("Can not find Company for employee"))

        settings = frappe.get_doc("Accounts Settings")
        # Load Salary Components
        basic_salary_component = settings.custom_basic_salary or None
        housing_allowance_component = settings.custom_housing_allowance or None
        transfer_allowance = settings.custom_transfer_allowance or None

        # Load Journal Accounts
        other_allowance_account = settings.custom_other_allowance or None
        end_of_service_account = settings.custom_end_of_service_award or None
        leave_account = settings.custom_vacation_expense or None
        accrual = settings.custom_end_of_service_accrual or None
        group_earnings_in = settings.custom_earning or None
        group_deductions_in = settings.custom_deductions or None
        cost_center = self.get_cost_center_for_employee()

        jv = frappe.new_doc("Journal Entry")
        jv.posting_date = nowdate()
        jv.voucher_type = "Journal Entry"
        salary_is_already_taken = cint(self.salary_is_already_taken)

        paid_amt = 0
        deduct_add_salary = False

        if group_earnings_in and flt(self.total_earning) > 0:
            account_type = frappe.get_cached_value(
                "Account", group_earnings_in, "account_type"
            )
            row = {
                "account": group_earnings_in,
                "debit_in_account_currency": flt(self.total_earning),
                "reference_type": "End of Service Award",
                "reference_name": self.name,
                "cost_center": cost_center,
            }
            if account_type in ["Receivable", "Payable"]:
                row.update({"party_type": "Employee", "party": self.employee})

            jv.append(
                "accounts",
                row,
            )

            paid_amt += flt(self.total_earning)

        if group_deductions_in and flt(self.total_deduction) > 0:
            account_type = frappe.get_cached_value(
                "Account", group_deductions_in, "account_type"
            )
            row = {
                "account": group_deductions_in,
                "debit_in_account_currency": -1 * flt(self.total_deduction),
                "reference_type": "End of Service Award",
                "reference_name": self.name,
                "cost_center": cost_center,
            }
            if account_type in ["Receivable", "Payable"]:
                row.update({"party_type": "Employee", "party": self.employee})
            jv.append(
                "accounts",
                row,
            )
            paid_amt -= flt(self.total_deduction)

        if flt(self.total_month_basic, 2) != 0 and salary_is_already_taken == 0:
            if not basic_salary_component:
                frappe.throw(
                    _("Please set salary component for Basic Salary in {0}").format(
                        get_link_to_form("Accounts Settings", "Accounts Settings")
                    )
                )

            account = self.get_salary_component_account(basic_salary_component, company)
            account_type = frappe.get_cached_value("Account", account, "account_type")

            amt = flt(self.total_month_basic)
            per_cent = flt(
                (flt(self.total_month_basic) * 100) / flt(self.total_month_salary)
            )
            if not group_earnings_in:
                amt += flt((per_cent * flt(self.total_earning)) / 100)
            if not group_deductions_in:
                amt -= flt((per_cent * flt(self.total_deduction)) / 100)

            row = {
                "account": account,
                "debit_in_account_currency": amt,
                "reference_type": "End of Service Award",
                "reference_name": self.name,
                "cost_center": cost_center,
            }
            if account_type in ["Receivable", "Payable"]:
                row.update({"party_type": "Employee", "party": self.employee})

            jv.append(
                "accounts",
                row,
            )
            paid_amt += flt(amt, 2)
            deduct_add_salary = True

        if flt(self.total_month_housing, 2) != 0 and salary_is_already_taken == 0:
            if not housing_allowance_component:
                frappe.throw(
                    _(
                        "Please set salary component for Housing Allownace in {0}"
                    ).format(get_link_to_form("Accounts Settings", "Accounts Settings"))
                )

            account = self.get_salary_component_account(
                housing_allowance_component, company
            )
            account_type = frappe.get_cached_value("Account", account, "account_type")

            amt = flt(self.total_month_housing)
            per_cent = flt(
                (flt(self.total_month_housing) * 100) / flt(self.total_month_salary)
            )
            if not group_earnings_in:
                amt += flt((per_cent * flt(self.total_earning)) / 100)
            if not group_deductions_in:
                amt -= flt((per_cent * flt(self.total_deduction)) / 100)

            row = {
                "account": account,
                "debit_in_account_currency": amt,
                "reference_type": "End of Service Award",
                "reference_name": self.name,
                "cost_center": cost_center,
            }
            if account_type in ["Receivable", "Payable"]:
                row.update({"party_type": "Employee", "party": self.employee})
            jv.append(
                "accounts",
                row,
            )
            paid_amt += flt(amt, 2)
            deduct_add_salary = True

        if (
            flt(self.total_month_transportation, 2) != 0
            and salary_is_already_taken == 0
        ):
            if not transfer_allowance:
                frappe.throw(
                    _(
                        "Please set salary component for Transfer Allownace in {0}"
                    ).format(get_link_to_form("Accounts Settings", "Accounts Settings"))
                )

            account = self.get_salary_component_account(transfer_allowance, company)
            account_type = frappe.get_cached_value("Account", account, "account_type")

            amt = flt(self.total_month_transportation)
            per_cent = flt(
                (flt(self.total_month_transportation) * 100)
                / flt(self.total_month_salary)
            )
            if not group_earnings_in:
                amt += flt((per_cent * flt(self.total_earning)) / 100)
            if not group_deductions_in:
                amt -= flt((per_cent * flt(self.total_deduction)) / 100)

            row = {
                "account": account,
                "debit_in_account_currency": amt,
                "reference_type": "End of Service Award",
                "reference_name": self.name,
                "cost_center": cost_center,
            }
            if account_type in ["Receivable", "Payable"]:
                row.update({"party_type": "Employee", "party": self.employee})

            jv.append(
                "accounts",
                row,
            )
            paid_amt += flt(amt, 2)
            deduct_add_salary = True

        if flt(self.total_month_other, 2) != 0 and salary_is_already_taken == 0:
            if not other_allowance_account:
                frappe.throw(
                    _("Please set account for Other Allowance in {0}").format(
                        get_link_to_form("Accounts Settings", "Accounts Settings")
                    )
                )
            account_type = frappe.get_cached_value(
                "Account", other_allowance_account, "account_type"
            )

            amt = flt(self.total_month_other)
            per_cent = flt(
                (flt(self.total_month_other) * 100) / flt(self.total_month_salary)
            )
            if not group_earnings_in:
                amt += flt((per_cent * flt(self.total_earning)) / 100)
            if not group_deductions_in:
                amt -= flt((per_cent * flt(self.total_deduction)) / 100)

            row = {
                "account": other_allowance_account,
                "debit_in_account_currency": amt,
                "reference_type": "End of Service Award",
                "reference_name": self.name,
                "cost_center": cost_center,
            }
            if account_type in ["Receivable", "Payable"]:
                row.update({"party_type": "Employee", "party": self.employee})
            jv.append(
                "accounts",
                row,
            )
            paid_amt += flt(amt, 2)
            deduct_add_salary = True

        if flt(self.leave_total_cost, 2) != 0 or not deduct_add_salary:
            if not leave_account:
                frappe.throw(
                    _("Please set account for Vacation Expense in {0}").format(
                        get_link_to_form("Accounts Settings", "Accounts Settings")
                    )
                )
            account_type = frappe.get_cached_value(
                "Account", leave_account, "account_type"
            )
            amt = flt(self.leave_total_cost)
            # update leave costs if salary not changed
            if not deduct_add_salary:
                if not group_earnings_in:
                    amt += flt(self.total_earning)
                if not group_deductions_in:
                    amt -= flt(self.total_deduction)
            if amt != 0:
                row = {
                    "account": leave_account,
                    "debit_in_account_currency": amt,
                    "reference_type": "End of Service Award",
                    "reference_name": self.name,
                    "cost_center": cost_center,
                }
                if account_type in ["Receivable", "Payable"]:
                    row.update({"party_type": "Employee", "party": self.employee})
                jv.append(
                    "accounts",
                    row,
                )
            paid_amt += amt

        if flt(self.award, 2) != 0:
            if not end_of_service_account:
                frappe.throw(
                    _("Please set account for End of Service Award in {0}").format(
                        get_link_to_form("Accounts Settings", "Accounts Settings")
                    )
                )

            account_type = frappe.get_cached_value(
                "Account", end_of_service_account, "account_type"
            )
            row = {
                "account": end_of_service_account,
                "debit_in_account_currency": flt(self.award),
                "reference_type": "End of Service Award",
                "reference_name": self.name,
                "cost_center": cost_center,
            }
            if account_type in ["Receivable", "Payable"]:
                row.update({"party_type": "Employee", "party": self.employee})
            jv.append(
                "accounts",
                row,
            )
            paid_amt += flt(self.award)
        if not accrual:
            frappe.throw(
                _("Please set account for End of service Accrual in {0}").format(
                    get_link_to_form("Accounts Settings", "Accounts Settings")
                )
            )
        account_type = frappe.get_cached_value("Account", accrual, "account_type")

        if paid_amt == 0:
            frappe.throw(_("Both Total Debit and Total Credit values cannot be zero"))

        row = {
            "account": accrual,
            "credit_in_account_currency": paid_amt,
            "reference_type": "End of Service Award",
            "reference_name": self.name,
            "cost_center": cost_center,
        }
        if account_type in ["Receivable", "Payable"]:
            row.update({"party_type": "Employee", "party": self.employee})
        jv.append(
            "accounts",
            row,
        )

        jv.flags.ignore_mandatory = True
        jv.save()
        frappe.msgprint(_("{0} {1} created").format(jv.doctype, jv.name))

    @frappe.whitelist()
    def make_bank_entry(self):
        if self.docstatus != 1:
            frappe.throw(_("Can not create journal entry"))
        jvs = end_of_service_has_bank_jv_entries(self.name, [0, 1])
        if jvs.get("submitted", 0) == 1:
            return jvs

        company = frappe.db.get_value("Employee", self.employee, "company")

        if not company:
            frappe.throw(_("Can not find Company for employee"))

        settings = frappe.get_doc("Accounts Settings")

        # Load Journal Accounts
        bank_account = settings.custom_bank_account or None
        accrual = settings.custom_end_of_service_accrual or None

        if not accrual:
            frappe.throw(
                _("Please set account for End of service Accrual in {0}").format(
                    get_link_to_form("Accounts Settings", "Accounts Settings")
                )
            )
        if not bank_account:
            frappe.throw(
                _("Please set account for Bank Account in {0}").format(
                    get_link_to_form("Accounts Settings", "Accounts Settings")
                )
            )
        jv = frappe.new_doc("Journal Entry")
        jv.posting_date = nowdate()
        jv.voucher_type = "Bank Entry"

        paid_amt = 0
        paid_amt += flt(self.total_month_basic)
        paid_amt += flt(self.total_month_housing)
        paid_amt += flt(self.total_month_transportation)
        paid_amt += flt(self.total_month_other)
        paid_amt += flt(self.leave_total_cost)
        paid_amt += flt(self.award)
        paid_amt -= flt(self.total_deduction)
        paid_amt += flt(self.total_earning)
        cost_center = self.get_cost_center_for_employee()
        if paid_amt == 0:
            frappe.throw(_("Both Total Debit and Total Credit values cannot be zero"))

        account_type = frappe.get_cached_value("Account", accrual, "account_type")
        row = {
            "account": accrual,
            "debit_in_account_currency": paid_amt,
            "reference_type": "End of Service Award",
            "reference_name": self.name,
            "cost_center": cost_center,
        }
        if account_type in ["Receivable", "Payable"]:
            row.update({"party_type": "Employee", "party": self.employee})

        jv.append(
            "accounts",
            row,
        )

        account_type = frappe.get_cached_value("Account", bank_account, "account_type")
        row = {
            "account": bank_account,
            "credit_in_account_currency": paid_amt,
            "reference_type": "End of Service Award",
            "reference_name": self.name,
            "cost_center": cost_center,
        }
        if account_type in ["Receivable", "Payable"]:
            row.update({"party_type": "Employee", "party": self.employee})

        jv.append(
            "accounts",
            row,
        )

        jv.flags.ignore_mandatory = True
        jv.save()
        frappe.msgprint(_("{0} {1} created").format(jv.doctype, jv.name))

    def get_salary_component_account(self, salary_component, company):
        account = frappe.db.get_value(
            "Salary Component Account",
            {"parent": salary_component, "company": company},
            "account",
        )

        if not account:
            frappe.throw(
                _("Please set account in Salary Component {0}").format(
                    get_link_to_form("Salary Component", salary_component)
                )
            )

        return account

    def get_cost_center_for_employee(self):
        if not hasattr(self, "employee_cost_centers"):
            self.employee_cost_centers = {}

        if not self.employee_cost_centers.get(self.employee):
            ss_assignment_name = frappe.db.get_value(
                "Salary Structure Assignment",
                {
                    "employee": self.employee,
                    "salary_structure": self.salary_structure,
                    "docstatus": 1,
                },
                "name",
            )

            if ss_assignment_name:
                cost_centers = dict(
                    frappe.get_all(
                        "Employee Cost Center",
                        {"parent": ss_assignment_name},
                        ["cost_center", "percentage"],
                        as_list=1,
                    )
                )
                if not cost_centers:
                    default_cost_center, department, company = frappe.get_cached_value(
                        "Employee",
                        self.employee,
                        ["payroll_cost_center", "department", "company"],
                    )
                    if not default_cost_center and department:
                        default_cost_center = frappe.get_cached_value(
                            "Department", department, "payroll_cost_center"
                        )
                    if not default_cost_center and company:
                        default_cost_center = frappe.get_cached_value(
                            "Company", company, "cost_center"
                        )

                    cost_centers = {default_cost_center: 100}

                self.employee_cost_centers.setdefault(self.employee, cost_centers)

        # return self.employee_cost_centers.get(self.employee, {})
        for k, v in self.employee_cost_centers.get(self.employee, {}).items():
            return k

    def get_format_currency(self, val, doc=None, currency=None, format=None):
        from frappe.utils.formatters import format_value

        fieldname = "other_allowance"
        df = self.meta.get_field(fieldname)
        if not df:
            from frappe.model.meta import get_default_df

            df = get_default_df(fieldname)

        if (
            df
            and df.fieldtype == "Currency"
            and not currency
            and (currency_field := df.get("options"))
            and (currency_value := self.get(currency_field))
        ):
            currency = frappe.db.get_value("Currency", currency_value, cache=True)

        if not doc:
            doc = getattr(self, "parent_doc", None) or self

        return format_value(val, df=df, doc=doc, currency=currency, format=format)

    def get_last_resignation(self):
        data = frappe.db.get_values(
            "Employee Resignation",
            {"employee": self.employee},
            ["approved_on", "date"],
            as_dict=True,
        )
        if len(data) == 0:
            return "", ""
        data = data[0]
        return data.date or "", data.approved_on or ""

    def get_day_name(self, date):
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        return _(days[getdate(date).weekday()], lang="ar")

    def get_money_words(self, amount, lang="en"):
        return money_in_words(amount, lang=lang)


@frappe.whitelist()
def get_award(start_date, end_date, salary, toc, reason):
    start = start_date
    end = end_date
    ret_dict = {}

    if not reason:
        ret_dict["award"] = 0
        return ret_dict

    if getdate(end) < getdate(start):
        frappe.throw("تاريخ نهاية العمل يجب أن يكون أكبر من تاريخ بداية العمل")
    else:
        diffDays = date_diff(end, start)
        years = math.floor(diffDays / 360)
        daysrem = diffDays - (years * 360)
        months = math.floor(daysrem / 30)
        days = math.ceil(daysrem - (months * 30))
        ret_dict = {"days": days, "months": months, "years": years, "award": 0}
    years = flt(years) + (flt(months) / 12) + (flt(days) / 360)
    if not reason:
        return
    else:
        if "كفالة فقط" in toc:
            if reason == "":
                ret_dict["award"] = 0
            else:
                firstPeriod = 0
                secondPeriod = 0
                if years > 5:
                    firstPeriod = 5
                    secondPeriod = years - 5
                else:
                    firstPeriod = years
                result = (firstPeriod * salary * 0.5) + (secondPeriod * salary)
                ret_dict["award"] = result
        else:

            if reason == "فسخ العقد":
                ret_dict["award"] = 0
            elif reason == "استقالة الموظف قبل انتهاء مدة العقد":
                if years < 2:
                    result = 0
                elif years <= 5:
                    result = (1.0 / 6.0) * salary * years
                elif years <= 10:
                    result = ((1.0 / 3.0) * salary * 5) + (
                        (2.0 / 3.0) * salary * (years - 5)
                    )
                else:
                    result = (0.5 * salary * 5) + (salary * (years - 5))
                ret_dict["award"] = result
            else:
                if years <= 5:
                    result = 0.5 * salary * years
                else:
                    result = (0.5 * salary * 5) + salary * (years - 5)
                ret_dict["award"] = result

    return ret_dict


def get_end_of_service_jv_entries(end_of_service_name, voucher_type, docstatus):
    je = frappe.qb.DocType("Journal Entry")
    jea = frappe.qb.DocType("Journal Entry Account")

    journal_entries = (
        frappe.qb.from_(je)
        .from_(jea)
        .select(je.name)
        .where(
            (je.name == jea.parent)
            & (je.voucher_type == voucher_type)
            & (je.docstatus.isin(docstatus))
            & (jea.reference_name == end_of_service_name)
            & (jea.reference_type == "End of Service Award")
        )
    ).run(as_dict=True)

    return journal_entries


@frappe.whitelist()
def end_of_service_has_jv_entries(name: str, docstatus=[1]):
    response = {}
    jvs = get_end_of_service_jv_entries(name, "Journal Entry", docstatus)
    response["submitted"] = 1 if jvs else 0

    return response


@frappe.whitelist()
def end_of_service_has_bank_jv_entries(name: str, docstatus=[1]):
    response = {}

    jvs_res = end_of_service_has_jv_entries(name, docstatus)
    if jvs_res.get("submitted", 0) == 0:
        response["submitted_jv"] = 0
        return response

    jvs = get_end_of_service_jv_entries(name, "Bank Entry", docstatus)
    response["submitted"] = 1 if jvs else 0

    return response


def money_in_words(
    number: str | float | int,
    main_currency: str | None = None,
    fraction_currency: str | None = None,
    lang="en",
):
    """
    Returns string in words with currency and fraction currency.
    """
    _ = frappe._

    try:
        # note: `flt` returns 0 for invalid input and we don't want that
        number = float(number)
    except ValueError:
        return ""

    number = flt(number)
    if number < 0:
        return ""

    d = get_defaults()
    if not main_currency:
        main_currency = d.get("currency", "INR")
    if not fraction_currency:
        fraction_currency = frappe.db.get_value(
            "Currency", main_currency, "fraction", cache=True
        ) or _("Cent", lang=lang)

    number_format = (
        frappe.db.get_value("Currency", main_currency, "number_format", cache=True)
        or frappe.db.get_default("number_format")
        or "#,###.##"
    )

    fraction_length = get_number_format_info(number_format)[2]

    n = f"%.{fraction_length}f" % number

    numbers = n.split(".")
    main, fraction = numbers if len(numbers) > 1 else [n, "00"]

    if len(fraction) < fraction_length:
        zeros = "0" * (fraction_length - len(fraction))
        fraction += zeros

    in_million = True
    if number_format == "#,##,###.##":
        in_million = False

    # 0.00
    if main == "0" and fraction in ["00", "000"]:
        out = (
            _(main_currency, context="Currency", lang=lang) + " " + _("Zero", lang=lang)
        )
    # 0.XX
    elif main == "0":
        out = (
            in_words(fraction, in_million, lang=lang).title() + " " + fraction_currency
        )
    else:
        out = (
            _(main_currency, context="Currency", lang=lang)
            + " "
            + in_words(main, in_million, lang=lang).title()
        )
        if cint(fraction):
            out = (
                out
                + " "
                + _("and", lang=lang)
                + " "
                + in_words(fraction, in_million, lang=lang).title()
                + " "
                + fraction_currency
            )

    return out


def in_words(integer: int, in_million=True, lang="en") -> str:
    """
    Returns string in words for the given integer.
    """
    from num2words import num2words

    integer = int(integer)
    try:
        ret = num2words(integer, lang=lang)
    except NotImplementedError:
        ret = num2words(integer, lang=lang)
    except OverflowError:
        ret = num2words(integer, lang=lang)
    return ret.replace("-", " ")


def get_number_format_info(format: str) -> tuple[str, str, int]:
    return number_format_info.get(format) or (".", ",", 2)


number_format_info = {
    "#,###.##": (".", ",", 2),
    "#.###,##": (",", ".", 2),
    "# ###.##": (".", " ", 2),
    "# ###,##": (",", " ", 2),
    "#'###.##": (".", "'", 2),
    "#, ###.##": (".", ", ", 2),
    "#,##,###.##": (".", ",", 2),
    "#,###.###": (".", ",", 3),
    "#.###": ("", ".", 0),
    "#,###": ("", ",", 0),
    "#.########": (".", "", 8),
}
