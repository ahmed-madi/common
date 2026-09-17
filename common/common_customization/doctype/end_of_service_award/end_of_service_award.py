# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from dateutil import relativedelta
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
)
from frappe.model.document import Document
from frappe.utils import (
    cint,
    date_diff,
    flt,
    get_defaults,
    get_link_to_form,
    getdate,
    now_datetime,
    nowdate,
)

# Helpers a reason's formula may call, on top of the award's own values.
FORMULA_GLOBALS = {
    "abs": abs,
    "cint": cint,
    "date_diff": date_diff,
    "flt": flt,
    "getdate": getdate,
    "max": max,
    "min": min,
    "round": round,
}

# What each name in get_formula_context() means, for the help shown on End of
# Service Award Reason. Kept next to the context itself - and tied to it by a
# test - so the documented variables cannot drift from the passed ones.
FORMULA_VARIABLES = {
    "salary": "Total monthly salary",
    "basic": "Basic salary",
    "housing_allowance": "Housing allowance",
    "transportation_allowance": "Transportation allowance",
    "other_allowance": "Other allowances",
    "years": "Length of service in years, as a fraction (years + months / 12 + days / 360)",
    "years_int": "Length of service, whole years only",
    "months": "Length of service, the months left over after the whole years",
    "days": "Length of service, the days left over after the whole months",
    "doc": "The whole End of Service Award - every field listed below, as doc.fieldname",
}


class EndofServiceAward(Document):
    def validate(self):
        # Single recalculation chain. Every total is derived on each save so the
        # server always agrees with what the form shows, no matter how the doc
        # was saved (UI, API, data import or a workflow transition).
        self.validate_dates()
        self.calculate_service_duration()
        self.calculate_days_number()
        self.calculate_salary_details()
        self.calculate_month_totals()
        self.calculate_leave_cost()
        self.calculate_ticket_cost()
        self.calculate_total_earning()
        self.calculate_total_deduction()
        self.get_award()
        self.calculate_total_award()

    def validate_dates(self):
        if not (self.end_date and self.work_start_date):
            return

        if getdate(self.end_date) < getdate(self.work_start_date):
            frappe.throw(
                _("End date must be greater than or equal to the work start date")
            )

    def calculate_service_duration(self):
        if not (self.end_date and self.work_start_date):
            self.years = self.months = self.days = 0
            return

        self.years, self.months, self.days = self.get_days_months_years(
            self.end_date, self.work_start_date
        )

    def dates_changed(self):
        """True when the employee or either service date differs from the saved doc."""
        previous = self.get_doc_before_save()
        if not previous:
            return True

        return any(
            self.get(field) != previous.get(field)
            for field in ("employee", "work_start_date", "end_date")
        )

    def calculate_days_number(self):
        """Number of unpaid days in the last month of service.

        Auto-filled whenever the employee or the service dates change, so it can
        never stay stale after a date edit, while still allowing a manual
        override to survive later saves that leave the dates alone.
        """
        if not (self.end_date and self.work_start_date):
            return

        if not self.dates_changed() and flt(self.days_number):
            return

        diff_days = date_diff(self.end_date, self.work_start_date) + 1
        if diff_days < 30:
            self.days_number = diff_days
        else:
            self.days_number = getdate(self.end_date).day

    def calculate_salary_details(self):
        if not self.employee:
            return

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
        self.housing_allowance = housing_allowance
        self.housing_day_value = housing_day_value
        self.transportation_allowance = transportation_allowance
        self.transportation_day_value = transportation_day_value
        # Other allowances are excluded from the award entirely -temporarily-,
        # so every field derived from them is forced to zero. Keeping the day
        # value non-zero used to leak the allowance into the journal entries
        # while `total` ignored it.
        self.other_allowance = 0
        self.other_day_value = 0

    def calculate_month_totals(self):
        """Last month's unpaid salary, per component.

        When the last month's salary has already been paid, every component is
        zeroed - not just `total_month_salary` - because the journal and bank
        entries post from the individual components.
        """
        if cint(self.salary_is_already_taken):
            self.total_month_salary = 0
            self.total_month_basic = 0
            self.total_month_housing = 0
            self.total_month_transportation = 0
            self.total_month_other = 0
            return

        days_number = flt(self.days_number)
        self.total_month_salary = flt(days_number * flt(self.day_value), 2)
        self.total_month_basic = flt(days_number * flt(self.basic_day_value), 2)
        self.total_month_housing = flt(days_number * flt(self.housing_day_value), 2)
        self.total_month_transportation = flt(
            days_number * flt(self.transportation_day_value), 2
        )
        self.total_month_other = flt(days_number * flt(self.other_day_value), 2)

    def calculate_leave_cost(self):
        """Leave balance and its cost.

        The balance is refetched whenever the employee or the service dates
        change; otherwise a manually entered balance is kept. The cost is always
        derived, so it can never drift from the balance times the day value.
        """
        if self.employee and self.work_start_date and self.end_date:
            if self.dates_changed() or not flt(self.leave_number):
                self.leave_number = self.get_leave_balance(
                    self.employee, self.work_start_date, self.end_date
                )

        self.leave_total_cost = flt(flt(self.leave_number) * flt(self.leave_cost), 2)

    def calculate_ticket_cost(self):
        self.ticket_total_cost = flt(flt(self.ticket_number) * flt(self.ticket_cost), 2)

    def get_award(self):
        """The award itself, from the formula (or fixed amount) on the reason.

        Every reason carries its own rule, so adding one is a matter of creating
        an End of Service Award Reason - no code change.
        """
        self.award = 0
        if not self.reason:
            self.exclude_award_from_total = 0
            return

        reason = frappe.get_cached_doc("End of Service Award Reason", self.reason)
        # Kept in step with the reason on every save, so the form and the
        # totals below never read a stale flag off a fetched field.
        self.exclude_award_from_total = cint(reason.exclude_award_from_total)

        if not reason.amount_based_on_formula:
            self.award = flt(reason.amount, 2)
            return

        self.award = flt(self.eval_formula(reason), 2)

    def eval_formula(self, reason):
        """Evaluate a reason's formula against this award.

        Errors name the reason and its formula - without that, a typo surfaces
        as a bare NameError on whatever award happens to be saved next.
        """
        try:
            # safe_eval writes its own builtins into the globals it is handed,
            # so it gets a copy rather than the shared module-level dict.
            return frappe.safe_eval(
                reason.formula, FORMULA_GLOBALS.copy(), self.get_formula_context()
            )
        except Exception as e:
            frappe.throw(
                _(
                    "Error evaluating the formula of reason {0}: {1}<br><pre>{2}</pre>"
                ).format(
                    get_link_to_form("End of Service Award Reason", reason.name),
                    e,
                    reason.formula,
                ),
                title=_("Invalid Formula"),
            )

    def get_formula_context(self):
        """The values a reason's formula may be written against."""
        years = cint(self.years) + cint(self.months) / 12 + cint(self.days) / 360

        return {
            # A plain dict, not the Document - a formula has no business
            # reaching the controller's methods.
            "doc": frappe._dict(self.as_dict()),
            "salary": flt(self.salary),
            "basic": flt(self.basic),
            "housing_allowance": flt(self.housing_allowance),
            "transportation_allowance": flt(self.transportation_allowance),
            "other_allowance": flt(self.other_allowance),
            "years": years,
            "years_int": cint(self.years),
            "months": cint(self.months),
            "days": cint(self.days),
        }

    @frappe.whitelist()
    def evaluate_award(self):
        """The award for the form, which cannot run a Python formula itself."""
        self.get_award()

        return {
            "award": flt(self.award),
            "exclude_award_from_total": cint(self.exclude_award_from_total),
        }

    def award_is_excluded(self):
        return cint(self.exclude_award_from_total)

    def get_component_share(self, component_amount):
        """A component's share of the last month's salary, as a percentage.

        Returns 0 when there is no last month's salary to apportion, instead of
        raising ZeroDivisionError.
        """
        total_month_salary = flt(self.total_month_salary)
        if not total_month_salary:
            return 0

        return flt((flt(component_amount) * 100) / total_month_salary)

    def get_payable_amount(self):
        """The net amount payable to the employee.

        Built from the same components used for the bank entry, and clamped
        exactly the way `total` is, so the bank entry and the `total` field can
        never disagree.
        """
        entitlements = (
            flt(self.total_month_basic)
            + flt(self.total_month_housing)
            + flt(self.total_month_transportation)
            + flt(self.total_month_other)
            + flt(self.leave_total_cost)
            + flt(self.ticket_total_cost)
            + flt(self.total_earning)
        )
        if not self.award_is_excluded():
            entitlements += flt(self.award)

        total_deduction = flt(self.total_deduction)
        if entitlements < total_deduction:
            return 0

        return flt(entitlements - total_deduction, 2)

    def calculate_total_award(self):
        totals = (
            flt(self.ticket_total_cost)
            + flt(self.total_month_salary)
            + flt(self.leave_total_cost)
            + flt(self.total_earning)
        )
        # Some reasons - the probation period among them - have the award shown
        # but not paid.
        if not self.award_is_excluded():
            totals += flt(self.award)

        total_deduction = flt(self.total_deduction)
        self.total = (
            flt(totals - total_deduction, 2) if totals >= total_deduction else 0
        )

    def calculate_total_deduction(self):
        rows = self.end_of_service_award_deduction or []
        self.total_deduction = flt(sum(flt(row.deduction) for row in rows), 2)

    def calculate_total_earning(self):
        rows = self.end_of_service_award_earning or []
        self.total_earning = flt(sum(flt(row.earning) for row in rows), 2)

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
            """.format(salary_slip),
            as_dict=True,
        )
        if not salary_details:
            frappe.throw(_("No salary found for this employee"))

        basic_components = []
        housing_components = []
        transportation_components = []
        for c in frappe.db.sql(
            "SELECT salary_component, type, parentfield from `tabHR Salary Component`",
            as_dict=True,
        ):
            if c.type == "Basic":
                basic_components.append(c.salary_component)
            elif c.type == "Housing Allowance":
                housing_components.append(c.salary_component)
            elif c.type == "Transportation Allowance":
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

        basic_day_value = flt(basic_salary / 30, 2)
        housing_day_value = flt(housing_allowance / 30, 2)
        transportation_day_value = flt(transportation_allowance / 30, 2)

        # The total day value is the sum of the component day values, not the
        # total rounded on its own. Rounding each one separately used to leave
        # `total_month_salary` a few cents away from the sum of the month
        # components, which in turn made the journal entry component shares add
        # up to slightly more or less than 100%.
        total_day_value = flt(
            basic_day_value + housing_day_value + transportation_day_value, 2
        )

        return (
            total_salary,
            total_day_value,
            basic_salary,
            basic_day_value,
            housing_allowance,
            housing_day_value,
            transportation_allowance,
            transportation_day_value,
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

    def get_annual_leave_type(self):
        """The leave type the award's leave balance is paid out from.

        Configured once in Company Policy, so the award never assumes what the
        annual leave type is named on this site.
        """
        leave_type = frappe.db.get_single_value("Company Policy", "annual_leave_type")
        if not leave_type:
            frappe.throw(
                _("Please set {0} in {1}").format(
                    frappe.bold(_("Annual Leave Type")),
                    get_link_to_form("Company Policy", "Company Policy"),
                )
            )
        return leave_type

    @frappe.whitelist()
    def get_leave_balance(self, employee, work_start_date, end_date):
        today = now_datetime().date()
        end = end_date
        leave_type = self.get_annual_leave_type()
        total_leave_balance = frappe.db.sql(
            """SELECT total_leaves_allocated, from_date, to_date, name
                FROM `tabLeave Allocation`
                WHERE employee=%(employee)s AND leave_type=%(leave_type)s
                AND docstatus = 1
                ORDER BY creation DESC LIMIT 1
                """,
            {"employee": employee, "leave_type": leave_type},
        )
        if total_leave_balance:
            leave_days = frappe.db.sql(
                """SELECT SUM(total_leave_days)
                FROM `tabLeave Application`
                WHERE employee=%(employee)s AND leave_type=%(leave_type)s
                AND posting_date BETWEEN %(from_date)s AND %(to_date)s""",
                {
                    "employee": employee,
                    "leave_type": leave_type,
                    "from_date": total_leave_balance[0][1],
                    "to_date": total_leave_balance[0][2],
                },
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

    def on_submit(self):
        self.close_out_employee_records()

    def close_out_employee_records(self):
        """Retire everything the employee is still active on.

        The order matters: leave allocations go before the policy assignment
        that created them - a submitted allocation links back to the assignment
        and frappe refuses to cancel a document that is still linked. The user
        is disabled before the employee is saved so Employee.update_user_status
        finds nothing left to do.
        """
        self.cancel_salary_structure_assignments()
        self.cancel_leave_policy_assignments()
        self.disable_employee_user()
        self.set_employee_as_left()

    def cancel_salary_structure_assignments(self):
        for name in frappe.get_all(
            "Salary Structure Assignment",
            filters={"employee": self.employee, "docstatus": 1},
            pluck="name",
        ):
            assignment = frappe.get_doc("Salary Structure Assignment", name)
            assignment.flags.ignore_permissions = True
            assignment.cancel()

    def cancel_leave_policy_assignments(self):
        for name in frappe.get_all(
            "Leave Policy Assignment",
            filters={"employee": self.employee, "docstatus": 1},
            pluck="name",
        ):
            for allocation_name in frappe.get_all(
                "Leave Allocation",
                filters={"leave_policy_assignment": name, "docstatus": 1},
                pluck="name",
            ):
                allocation = frappe.get_doc("Leave Allocation", allocation_name)
                allocation.flags.ignore_permissions = True
                # Cancelling the allocation also cancels its Leave Ledger
                # Entries, so the balance is reversed with it.
                allocation.cancel()

            assignment = frappe.get_doc("Leave Policy Assignment", name)
            assignment.flags.ignore_permissions = True
            assignment.cancel()

    def disable_employee_user(self):
        user_id = frappe.db.get_value("Employee", self.employee, "user_id")
        if not user_id:
            return

        if not frappe.db.get_value("User", user_id, "enabled"):
            return

        user = frappe.get_doc("User", user_id)
        user.enabled = 0
        user.save(ignore_permissions=True)

    def set_employee_as_left(self):
        employee = frappe.get_doc("Employee", self.employee)
        if employee.status == "Left" and employee.relieving_date:
            return

        employee.status = "Left"
        employee.relieving_date = self.end_date
        # Employee.validate_status throws when active employees still report to
        # this one - that error is left to surface, so the award is not
        # submitted against a half retired employee.
        employee.save(ignore_permissions=True)

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
            per_cent = self.get_component_share(self.total_month_basic)
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
            per_cent = self.get_component_share(self.total_month_housing)
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
            per_cent = self.get_component_share(self.total_month_transportation)
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
            per_cent = self.get_component_share(self.total_month_other)
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

        # The ticket cost is part of `total`, so it has to be posted too or the
        # journal entry and the bank entry would never reconcile. There is no
        # dedicated setting for it yet, so it falls back to the vacation expense
        # account - the same catch-all this method already uses - and will pick
        # up a `custom_ticket_expense` account automatically if one is added.
        if flt(self.ticket_total_cost, 2) != 0:
            ticket_account = settings.get("custom_ticket_expense") or leave_account
            if not ticket_account:
                frappe.throw(
                    _("Please set account for Vacation Expense in {0}").format(
                        get_link_to_form("Accounts Settings", "Accounts Settings")
                    )
                )
            account_type = frappe.get_cached_value(
                "Account", ticket_account, "account_type"
            )
            row = {
                "account": ticket_account,
                "debit_in_account_currency": flt(self.ticket_total_cost),
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
            paid_amt += flt(self.ticket_total_cost)

        if flt(self.award, 2) != 0 and not self.award_is_excluded():
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

        # Derived from the same components the journal entry posts, so the two
        # entries and the `total` field always reconcile. The month components
        # are already zeroed when the last month's salary was paid, the award is
        # excluded during probation, and the ticket cost is included.
        paid_amt = self.get_payable_amount()
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
