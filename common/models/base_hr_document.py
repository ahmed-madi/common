import frappe
from frappe import _
from frappe.utils import getdate, get_link_to_form, cstr, strip_html
from frappe.model.document import Document
from frappe.model import table_fields

from hrms.hr.utils import validate_active_employee


class BaseHRDocument(Document):
    def validate(self):
        if hasattr(super(), "validate"):
            super().validate()

        self.validate_active_employee()
        self.validate_status()

    def validate_active_employee(self):
        validate_active_employee(self.employee)

    def validate_backdate_restriction(
        self, restrict_check_field, whitelist_role_field, date_to_check=None
    ):
        restrict_backdated = frappe.db.get_single_value(
            "Company Policy", restrict_check_field
        )
        if date_to_check and getdate(date_to_check) >= getdate():
            return

        if not restrict_backdated:
            return
        whitelist_role = frappe.get_all(
            "Company Policy Whitelist Role",
            filters={
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
                    get_link_to_form(
                        "Company Policy", "Company Policy", _("Company Policy")
                    ),
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
