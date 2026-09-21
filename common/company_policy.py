# Copyright (c) 2026, Ahmed Madi and contributors
# For license information, please see license.txt

"""Reading Company Policy, which is configured per company.

A group can run companies in more than one country, under different labour law
and different HR rules, so there is a policy per company rather than one for
the site. Everything reads it through here: a call site names the setting it
wants and the company it wants it for, and never has to know how a policy is
stored or found.
"""

import frappe
from frappe import _
from frappe.utils import get_link_to_form


def get_policy_name(company=None):
    """The policy that applies to a company.

    Falls back for the callers that genuinely have no company in scope - a
    site-wide setting page, a scheduled job - first to the session's default
    company, then to the only policy there is. A site with several and no
    company to go on is a question nobody can answer, so it says so.
    """
    if company and frappe.db.exists("Company Policy", company):
        return company

    if company:
        frappe.throw(
            _("No Company Policy exists for {0}. Please create one.").format(
                frappe.bold(company)
            ),
            title=_("Company Policy Missing"),
        )

    default_company = frappe.defaults.get_user_default("Company")
    if default_company and frappe.db.exists("Company Policy", default_company):
        return default_company

    policies = frappe.get_all("Company Policy", pluck="name", limit=2)
    if len(policies) == 1:
        return policies[0]

    if not policies:
        frappe.throw(
            _("No Company Policy has been created yet."),
            title=_("Company Policy Missing"),
        )

    frappe.throw(
        _("This site has a {0} per company. Please say which company applies.").format(
            get_link_to_form("Company Policy", policies[0], _("Company Policy"))
        ),
        title=_("Company Required"),
    )


def get_policy(company=None):
    """The whole policy for a company, cached."""
    return frappe.get_cached_doc("Company Policy", get_policy_name(company))


def get_policy_value(fieldname, company=None):
    """One setting from a company's policy.

    The replacement for get_single_value("Company Policy", fieldname), which
    could only ever have answered for one company.
    """
    return frappe.get_cached_value(
        "Company Policy", get_policy_name(company), fieldname
    )


def get_employee_policy(employee):
    """The policy that applies to an employee, through their company."""
    company = frappe.db.get_value("Employee", employee, "company") if employee else None

    return get_policy(company)


@frappe.whitelist()
def get_value_for_employee(fieldname, employee=None, company=None):
    """A setting, for a form that needs it before it has saved anything.

    Whitelisted because the client cannot read a policy directly any more - it
    has to say which company, and only the server knows an employee's.
    """
    frappe.has_permission("Company Policy", throw=True)

    if not company and employee:
        company = frappe.db.get_value("Employee", employee, "company")

    return get_policy_value(fieldname, company)
