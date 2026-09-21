# Copyright (c) 2026, Ahmed Madi and contributors
# For license information, please see license.txt

"""The figures the Employee record carries from elsewhere.

An employee's salary lives on their last payslip and their leave balance in
their allocations, but both are asked for often enough - on the employee's own
page, in a salary identification letter, in a report - that recomputing them
every time is wasteful. They are kept on the Employee and refreshed by the
documents that change them.

Which salary component counts as basic, housing or transportation is configured
once in Company Policy, and read from there everywhere.
"""

import frappe
from frappe import _
from frappe.utils import flt, get_link_to_form, nowdate

from common.company_policy import get_policy, get_policy_value

# The categories Company Policy can classify a salary component into, and the
# field on Employee each one totals into.
CATEGORY_FIELDS = {
    "Basic": "custom_basic_salary",
    "Housing Allowance": "custom_housing_allowance",
    "Transportation Allowance": "custom_transportation_allowance",
}

# Anything a site has not classified - and anything classified as a category
# this app no longer recognises - is an other allowance.
OTHER_FIELD = "custom_other_allowances"

LEAVE_BALANCE_FIELD = "custom_annual_leave_balance"

SNAPSHOT_FIELDS = [*CATEGORY_FIELDS.values(), OTHER_FIELD]


def get_employee_company(employee):
    return frappe.db.get_value("Employee", employee, "company") if employee else None


def get_component_types(company=None):
    """Each salary component's category, as Company Policy has it configured.

    Keyed by company, so two companies may classify the same component
    differently - which is the point of a policy per company.
    """
    policy = get_policy(company)

    return {
        row.salary_component: row.type
        for row in (policy.salary_component_categories or [])
        if row.salary_component and row.type
    }


def classify(amounts, company=None):
    """Total a set of component amounts into the Employee's salary fields.

    A component nobody has classified falls into other allowances rather than
    being dropped, so an employee's parts always add up to their whole.
    """
    types = get_component_types(company)
    totals = dict.fromkeys(SNAPSHOT_FIELDS, 0.0)

    for component, amount in amounts.items():
        field = CATEGORY_FIELDS.get(types.get(component), OTHER_FIELD)
        totals[field] = flt(totals[field]) + flt(amount)

    return totals


def get_latest_salary_slip(employee):
    slips = frappe.get_all(
        "Salary Slip",
        filters={"employee": employee, "docstatus": 1},
        fields=["name"],
        order_by="start_date desc, creation desc",
        limit=1,
    )

    return slips[0].name if slips else None


def get_salary_slip_earnings(salary_slip):
    rows = frappe.get_all(
        "Salary Detail",
        filters={
            "parent": salary_slip,
            "parentfield": "earnings",
            "parenttype": "Salary Slip",
        },
        fields=["salary_component", "amount"],
    )

    amounts = {}
    for row in rows:
        amounts[row.salary_component] = flt(amounts.get(row.salary_component)) + flt(
            row.amount
        )

    return amounts


def get_salary_snapshot(employee):
    """The employee's salary by category, from their latest submitted payslip.

    Recomputed rather than read, so it is the one place the figures are derived
    and every caller agrees on them.
    """
    salary_slip = get_latest_salary_slip(employee)
    if not salary_slip:
        return dict.fromkeys(SNAPSHOT_FIELDS, 0.0)

    return classify(
        get_salary_slip_earnings(salary_slip), get_employee_company(employee)
    )


def get_annual_leave_balance(employee):
    """The employee's remaining balance of the leave type Company Policy names.

    Returns None when no annual leave type is configured - a missing setting is
    not a zero balance, and writing zero would read as one.
    """
    from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on

    leave_type = get_policy_value("annual_leave_type", get_employee_company(employee))
    if not leave_type:
        return None

    return flt(get_leave_balance_on(employee, leave_type, nowdate()))


def update_employee(employee, salary=True, leave=True):
    """Refresh what the Employee carries, without touching the rest of it.

    Written with db_set so refreshing a figure never runs the Employee's own
    validation - an employee whose record has an unrelated problem should still
    have an accurate balance.
    """
    if not employee or not frappe.db.exists("Employee", employee):
        return

    values = {}

    if salary:
        values.update(get_salary_snapshot(employee))

    if leave:
        balance = get_annual_leave_balance(employee)
        if balance is not None:
            values[LEAVE_BALANCE_FIELD] = balance

    if not values:
        return

    frappe.db.set_value("Employee", employee, values, update_modified=False)


def get_annual_leave_type(company=None):
    """The configured annual leave type, or a linked error naming the setting."""
    policy = get_policy(company)
    if not policy.annual_leave_type:
        frappe.throw(
            _("Please set {0} in {1}").format(
                frappe.bold(_("Annual Leave Type")),
                get_link_to_form("Company Policy", policy.name),
            )
        )

    return policy.annual_leave_type
