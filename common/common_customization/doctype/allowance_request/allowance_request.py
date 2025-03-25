# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, flt, cint, nowdate, add_months, get_link_to_form


class AllowanceRequest(Document):
    def before_validate(self):
        self.load_latest_request_type()

    def validate(self):
        self.validate_dates(self.posting_date)
        self.validate_if_old_request()

    def before_cancel(self):
        self.flags.ignore_links = True
        self.db_set("bank_entry", "")

    def validate_if_old_request(self):
        allowed_requests = cint(frappe.db.get_value("Gift Request Type", self.request_type, "allowed_requests"))
        if allowed_requests == 0:
            return
        year_ago = add_months(self.posting_date, -12)
        other_requests = frappe.db.sql(
            """
                SELECT name, posting_date, employee FROM `tabAllowance Request`
                WHERE request_type='{}' AND employee='{}' AND docstatus=1 AND name!='{}'
                        AND posting_date >= '{}' AND posting_date <= '{}'
                ORDER BY posting_date DESC
            """.format(
                self.request_type, self.employee, self.name, year_ago, self.posting_date
            ),
            as_dict=True,
        )
        if len(other_requests) >= allowed_requests:
            frappe.throw(_("You have exceeded the maximum number of requests allowed."))

    def validate_dates(self, posting_date):
        if not posting_date:
            frappe.throw(_("Posting date is Mandatory"))
        posting_date = getdate(posting_date)
        date_of_joining = frappe.get_value("Employee", self.employee, "date_of_joining")
        diff = date_diff(posting_date, date_of_joining)
        if diff < 90:
            frappe.throw(_("Can not make request before 90 of joining"))

    def load_latest_request_type(self):
        values = frappe.db.get_values(
            "Gift Request Type",
            self.request_type,
            ["add_to", "salary_component", "total_months", "allowed_requests"],
            as_dict=True,
        )
        if len(values) == 0:
            return

        values = values[0]
        self.add_to = values.add_to
        self.salary_component = values.salary_component

    def on_submit(self):
        if self.add_to != "Additional Salary":
            return

        total_months = cint(frappe.db.get_value("Gift Request Type", self.request_type, "total_months") or 1)

        add_sal = frappe.new_doc("Additional Salary")
        add_sal.employee = self.employee
        add_sal.is_recurring = 1
        add_sal.overwrite_salary_structure_amount = 1
        add_sal.salary_component = self.salary_component
        add_sal.amount = flt(self.gift_cost)
        add_sal.from_date = add_months(self.posting_date, 1)
        add_sal.to_date = add_months(self.posting_date, (total_months + 1))
        add_sal.flags.ignore_mandatory = True
        add_sal.save()
        add_sal.submit()

    @frappe.whitelist()
    def make_journal_entry(self):
        if self.docstatus != 1:
            frappe.throw(_("Can not create journal entry for draft request"))

        if self.add_to != "Journal Entry" or flt(self.gift_cost) == 0:
            frappe.throw(_("Can not create journal entry"))

        submitted = 0
        drafts = 0

        for jv in get_jv_entries(self.name, "Journal Entry"):
            if jv.docstatus == 1:
                submitted += flt(jv.debit_in_account_currency) + flt(jv.credit_in_account_currency)
            if jv.docstatus == 0:
                drafts += flt(jv.debit_in_account_currency) + flt(jv.credit_in_account_currency)

        if (submitted + drafts) >= flt(self.gift_cost):
            return

        amt = flt(flt(self.gift_cost) - (submitted + drafts), 2)

        accounts_values = frappe.db.get_values(
            "Accounts Settings",
            "Accounts Settings",
            ["custom_debit_account", "custom_credit_account"],
            as_dict=True,
        )
        if len(accounts_values) == 0:
            frappe.throw(
                _("Please set Debit and Credit Accounts for Allowance Request in {0}").format(
                    get_link_to_form("Accounts Settings", "Accounts Settings")
                )
            )
        debit_account = accounts_values[0].get("custom_debit_account")
        credit_account = accounts_values[0].get("custom_credit_account")

        if not debit_account or debit_account is None or not credit_account or credit_account is None:
            frappe.throw(
                _("Please set Debit and Credit Accounts for Allowance Request in {0}").format(
                    get_link_to_form("Accounts Settings", "Accounts Settings")
                )
            )
        debit_account_type = frappe.get_cached_value("Account", debit_account, "account_type")
        credit_account_type = frappe.get_cached_value("Account", credit_account, "account_type")

        company = frappe.db.get_value("Employee", self.employee, "company")
        if not company:
            frappe.throw(_("Can not find Company for employee"))

        jv = frappe.new_doc("Journal Entry")
        jv.posting_date = nowdate()
        jv.voucher_type = "Journal Entry"

        row = {
            "account": debit_account,
            "debit_in_account_currency": amt,
            "reference_type": "Allowance Request",
            "reference_name": self.name,
        }
        if debit_account_type in ["Receivable", "Payable"]:
            row.update({"party_type": "Employee", "party": self.employee})
        jv.append("accounts", row)
        row = {
            "account": credit_account,
            "credit_in_account_currency": amt,
            "reference_type": "Allowance Request",
            "reference_name": self.name,
        }
        if credit_account_type in ["Receivable", "Payable"]:
            row.update({"party_type": "Employee", "party": self.employee})
        jv.append("accounts", row)
        jv.title = "Allowance Request {}".format(self.name)
        jv.flags.ignore_mandatory = True
        jv.save()
        frappe.msgprint(_("{0} {1} created").format(jv.doctype, jv.name))

    @frappe.whitelist()
    def make_bank_entry(self):
        if self.docstatus != 1:
            frappe.throw(_("Can not create journal entry"))

        if self.bank_entry:
            return

        result = get_jv_entries(self.name, "Bank Entry")
        if len(result) > 0:
            return

        company = frappe.db.get_value("Employee", self.employee, "company")

        if not company:
            frappe.throw(_("Can not find Company for employee"))

        settings = frappe.get_doc("Accounts Settings")

        # Get Accounts
        debit_bank_account = settings.custom_bank_debit_account or None
        credit_bank_account = settings.custom_bank_credit_account or None

        if not debit_bank_account:
            frappe.throw(
                _("Please set account for End of service Accrual in {0} in Tab Allowance Request").format(
                    get_link_to_form("Accounts Settings", "Accounts Settings")
                )
            )
        if not credit_bank_account:
            frappe.throw(
                _("Please set account for Bank Account in {0} in Tab Allowance Request").format(
                    get_link_to_form("Accounts Settings", "Accounts Settings")
                )
            )

        jv = frappe.new_doc("Journal Entry")
        jv.posting_date = nowdate()
        jv.voucher_type = "Bank Entry"

        paid_amt = flt(self.gift_cost)
        cost_center = None

        if paid_amt == 0:
            frappe.throw(_("Both Total Debit and Total Credit values cannot be zero"))

        row = {
            "account": debit_bank_account,
            "debit_in_account_currency": paid_amt,
            "reference_type": "Allowance Request",
            "reference_name": self.name,
            "cost_center": cost_center,
            "party_type": "Employee",
            "party": self.employee,
        }

        jv.append(
            "accounts",
            row,
        )

        row = {
            "account": credit_bank_account,
            "credit_in_account_currency": paid_amt,
            "reference_type": "Allowance Request",
            "reference_name": self.name,
            "cost_center": cost_center,
        }
        jv.append(
            "accounts",
            row,
        )

        jv.flags.ignore_mandatory = True
        jv.save()
        self.db_set("bank_entry", jv.name)
        frappe.msgprint(_("{0} {1} created").format(jv.doctype, jv.name))


@frappe.whitelist()
def has_jv_entries(name: str):
    name = frappe.db.exists("Allowance Request", name)
    if not name:
        return {"make_jv": 0}
    values = frappe.db.get_values("Allowance Request", name, ["add_to", "gift_cost"], as_dict=True)
    if len(values) == 0:
        return {"make_jv": 0}
    values = values[0]
    add_to = values.add_to
    gift_cost = flt(values.gift_cost)

    if add_to != "Journal Entry" or gift_cost == 0:
        return {"make_jv": 0}

    submitted = 0
    drafts = 0
    for jv in get_jv_entries(name, "Journal Entry"):
        if jv.docstatus == 1:
            submitted += flt(jv.debit_in_account_currency) + flt(jv.credit_in_account_currency)
        if jv.docstatus == 0:
            drafts += flt(jv.debit_in_account_currency) + flt(jv.credit_in_account_currency)

    if submitted >= gift_cost:
        return {"make_jv": 0}

    return {"make_jv": 1}


def get_jv_entries(name, voucher_type):
    je = frappe.qb.DocType("Journal Entry")
    jea = frappe.qb.DocType("Journal Entry Account")

    journal_entries = (
        frappe.qb.from_(je)
        .from_(jea)
        .select(jea.docstatus)
        .select(jea.debit_in_account_currency)
        .select(jea.credit_in_account_currency)
        .where(
            (je.name == jea.parent)
            & (je.voucher_type == voucher_type)
            & (je.docstatus.isin([0, 1]))
            & (jea.reference_name == name)
            & (jea.reference_type == "Allowance Request")
        )
    ).run(as_dict=True)

    return journal_entries
