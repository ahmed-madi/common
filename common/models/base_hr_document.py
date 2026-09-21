import frappe
from frappe import _
from frappe.model import table_fields
from frappe.model.document import Document
from frappe.utils import cstr, get_link_to_form, getdate, strip_html
from hrms.hr.utils import validate_active_employee

from common.company_policy import get_policy, get_policy_value


class BaseHRDocument(Document):
    def validate(self):
        if hasattr(super(), "validate"):
            super().validate()

        self.validate_active_employee()
        self.validate_status()

    def validate_active_employee(self):
        validate_active_employee(self.employee)

    def policy_company(self):
        """The company whose HR rules apply to this document.

        Company Policy is configured per company, so every rule this document
        obeys is its employee's company's rule. Resolved once and kept on the
        document - it is asked for several times in a single validate().
        """
        if self.get("company"):
            return self.company

        if self.flags.get("policy_company") is None:
            self.flags.policy_company = (
                frappe.db.get_value("Employee", self.employee, "company")
                if self.employee
                else None
            )

        return self.flags.policy_company

    def get_policy(self):
        return get_policy(self.policy_company())

    def policy_value(self, fieldname):
        return get_policy_value(fieldname, self.policy_company())

    def validate_backdate_restriction(
        self, restrict_check_field, whitelist_role_field, date_to_check=None
    ):
        policy = self.get_policy()
        restrict_backdated = policy.get(restrict_check_field)
        if date_to_check and getdate(date_to_check) >= getdate():
            return

        if not restrict_backdated:
            return
        # Scoped to this company's policy. Without the parent, every
        # company's whitelist would answer for every other.
        whitelist_role = frappe.get_all(
            "Company Policy Whitelist Role",
            filters={
                "parent": policy.name,
                "parenttype": "Company Policy",
                "parentfield": whitelist_role_field,
            },
            pluck="role",
        )
        doc = self.doctype.lower()
        if not whitelist_role:
            frappe.throw(
                _("Backdated in {0} is restricted. Please set the {1} in {2}").format(
                    _(doc),
                    frappe.bold(_("{} Whitelist Role".format(self.doctype))),
                    get_link_to_form("Company Policy", policy.name, _("Company Policy")),
                )
            )
        # user_roles = frappe.get_roles(frappe.session.user)
        # for role in user_roles:
        #     if role in whitelist_role:
        #         return
        if date_to_check and getdate(date_to_check) < getdate():
            whitelist_role = "".join(
                ["<li>{}</li>".format(frappe.bold(_(r))) for r in whitelist_role]
            )
            whitelist_role = f"<br /><br /><ul>{whitelist_role}</ul>"
            frappe.throw(
                _(
                    "Only users with the following roles can create backdated in {} {}"
                ).format(
                    _(doc),
                    whitelist_role,
                )
            )

    def validate_status(self):
        if not hasattr(self, "status"):
            return

        if self.docstatus == 1 and self.status in ["Open", "Cancelled"]:
            frappe.throw(
                _(
                    "Only Applications with status 'Approved' and 'Rejected' can be submitted"
                )
            )

    def validate_from_to_dates(
        self, from_date=None, to_date=None, msg="To date cannot be before from date"
    ):
        if from_date and to_date and (getdate(to_date) < getdate(from_date)):
            frappe.throw(_(msg))

    def before_cancel(self):
        if hasattr(super(), "before_cancel"):
            super().before_cancel()

        if hasattr(self, "status"):
            self.db_set("status", "Cancelled")

    def get_msg(self, df):
        if df.fieldtype in table_fields:
            return "{}: {}: {}".format(
                _("Error"), _("Data missing in table"), _(df.label, context=df.parent)
            )

        # check if parentfield exists (only applicable for child table doctype)
        elif self.get("parentfield"):
            return "{}: {} {} #{}: {}: {}".format(
                _("Error"),
                frappe.bold(_(self.doctype)),
                _("Row"),
                self.idx,
                _("Value missing for"),
                _(df.label, context=df.parent),
            )

        return _("Error: Value missing for {0}: {1}").format(
            _(df.parent), _(df.label, context=df.parent)
        )

    def has_content(self, df):
        value = cstr(self.get(df.fieldname))
        has_text_content = strip_html(value).strip()
        has_img_tag = "<img" in value
        has_text_or_img_tag = has_text_content or has_img_tag

        if df.fieldtype == "Text Editor" and has_text_or_img_tag:
            return True
        elif df.fieldtype == "Code" and df.options == "HTML" and has_text_or_img_tag:
            return True
        else:
            return has_text_content
