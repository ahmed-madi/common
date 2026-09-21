# Copyright (c) 2026, Ahmed Madi and contributors
# For license information, please see license.txt

"""Building and sending the salary identification letter.

Kept beside the controller rather than in it: the controller's job is the
document's lifecycle, and this is the letter itself - what it says, who it
goes to, and the print format it prints on.
"""

import frappe
from frappe import _
from frappe.utils import flt, get_link_to_form, now_datetime

from common.company_policy import get_employee_policy, get_policy
from common.employee_snapshot import (
    CATEGORY_FIELDS,
    OTHER_FIELD,
    SNAPSHOT_FIELDS,
    get_salary_snapshot,
)

# Each salary line the letter can show, the Company Policy switch that decides
# whether it appears, and the Employee field it reads.
SALARY_LINES = [
    ("Housing Allowance", "include_housing_in_sidl", CATEGORY_FIELDS["Housing Allowance"]),
    (
        "Transportation Allowance",
        "include_transportation_in_sidl",
        CATEGORY_FIELDS["Transportation Allowance"],
    ),
    ("Other Allowances", "include_other_in_sidl", OTHER_FIELD),
]

BASIC_FIELD = CATEGORY_FIELDS["Basic"]
BASIC_SWITCH = "include_basic_in_sidl"

# In the order the employee's own email should be looked for.
EMAIL_FIELDS = ("prefered_email", "company_email", "personal_email")


def get_salary_breakdown(employee):
    """The salary lines the letter shows, as Company Policy has them configured.

    The amounts come from the Employee, which every submitted payslip keeps
    current, so the letter and the employee's own page can never quote
    different figures. An employee whose snapshot has never been written - one
    hired before this existed, say - is computed on the spot instead of being
    shown zeroes.
    """
    values = frappe.db.get_value("Employee", employee, SNAPSHOT_FIELDS, as_dict=True) or {}
    if not any(flt(value) for value in values.values()):
        values = get_salary_snapshot(employee)

    policy = get_employee_policy(employee)

    basic = flt(values.get(BASIC_FIELD)) if policy.get(BASIC_SWITCH) else 0
    allowances = [
        {"label": _(label), "amount": flt(values.get(field))}
        for label, switch, field in SALARY_LINES
        if policy.get(switch) and flt(values.get(field))
    ]

    return {
        "basic": basic,
        "allowances": allowances,
        # The total covers only what the letter actually discloses, so it can
        # never be read as a figure the lines below it fail to add up to.
        "total": basic + sum(flt(row["amount"]) for row in allowances),
    }


def get_employee_bank_account(employee):
    """The employee's default bank account, for the letter's account row."""
    banks = frappe.get_all(
        "Employee Bank",
        filters={"parent": employee, "parenttype": "Employee"},
        fields=["iban", "bank_ac_no", "default"],
        order_by="`default` desc, idx asc",
        limit=1,
    )
    if not banks:
        return frappe.db.get_value("Employee", employee, "iban") or ""

    return banks[0].iban or banks[0].bank_ac_no or ""


def get_employee_email(employee):
    """Where the letter goes.

    prefered_email first, because it is the address the employee themselves
    chose through prefered_contact_email.
    """
    values = frappe.db.get_value(
        "Employee", employee, [*EMAIL_FIELDS, "user_id", "employee_name"], as_dict=True
    )

    for field in EMAIL_FIELDS:
        if values.get(field):
            return values[field]

    if values.get("user_id"):
        return frappe.db.get_value("User", values.user_id, "email")

    return None


def get_print_format(company):
    """The print format this company's letter prints on.

    Every company has its own letterhead, so the format is configured per
    company. A company with no row gets no automatic letter - that is the
    switch for turning the automation off for one company.
    """
    policy = get_policy(company)

    for row in policy.sidl_print_formats or []:
        if row.company == company:
            return row.print_format

    return None


def send_letter(name):
    """Render the letter, attach it, and email it to the employee.

    Runs in the background after the approval has committed, so a print or mail
    failure can never undo the approval itself.
    """
    doc = frappe.get_doc("Salary Identification Letter", name)

    if doc.letter_sent_on:
        return

    print_format = get_print_format(doc.company)
    if not print_format:
        skip(
            doc,
            _("No print format is configured for {0} in {1}, so the letter was not sent.").format(
                frappe.bold(doc.company),
                get_link_to_form("Company Policy", doc.company, _("Company Policy")),
            ),
        )
        return

    recipient = get_employee_email(doc.employee)
    if not recipient:
        skip(
            doc,
            _("No email address is set for {0}, so the letter was not sent.").format(
                get_link_to_form("Employee", doc.employee, doc.employee_name)
            ),
        )
        return

    attachment = frappe.attach_print(
        doc.doctype,
        doc.name,
        print_format=print_format,
        doc=doc,
        lang=doc.preferred_language,
        letterhead=frappe.db.get_value("Company", doc.company, "default_letter_head"),
    )

    # Kept on the document, so there is a record of exactly what was sent rather
    # than a letter that has to be regenerated from data that may have moved on.
    letter_file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": attachment["fname"],
            "content": attachment["fcontent"],
            "attached_to_doctype": doc.doctype,
            "attached_to_name": doc.name,
            "is_private": 1,
        }
    ).insert(ignore_permissions=True)

    frappe.sendmail(
        recipients=[recipient],
        subject=_("Salary Identification Letter"),
        message=_(
            "Dear {0},<br><br>"
            "Please find your salary identification letter attached.<br><br>"
            "Regards,<br>{1}"
        ).format(doc.employee_name, doc.company),
        attachments=[{"fid": letter_file.name}],
        reference_doctype=doc.doctype,
        reference_name=doc.name,
    )

    doc.db_set("letter_sent_on", now_datetime(), update_modified=False)


def skip(doc, reason):
    """Record why no letter went out.

    Approval is not blocked by a configuration gap, but nobody should have to
    guess why an employee never received anything.
    """
    doc.add_comment("Comment", reason)
    frappe.db.commit()


def get_letter_context(doc):
    """Everything the print format needs, gathered in one call.

    The template asks for this once rather than reaching into the database line
    by line, so what the letter can say is decided here and stays testable.
    """
    if isinstance(doc, str):
        doc = frappe.get_doc("Salary Identification Letter", doc)

    employee = frappe.get_cached_doc("Employee", doc.employee)

    return frappe._dict(
        {
            "employee": employee,
            "nationality": employee.get("custom_nationality") or "",
            "national_id": employee.get("custom_national_id") or "",
            "employee_number": employee.get("employee_number") or "",
            "designation": employee.get("designation") or "",
            "date_of_joining": employee.get("date_of_joining"),
            "bank_account": get_employee_bank_account(doc.employee),
            "salary": get_salary_breakdown(doc.employee),
        }
    )
