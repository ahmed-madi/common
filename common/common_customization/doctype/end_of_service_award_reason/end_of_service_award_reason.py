# Copyright (c) 2026, Ahmed Madi and contributors
# For license information, please see license.txt

import ast

import frappe
from frappe import _
from frappe.model import no_value_fields
from frappe.model.document import Document


class EndofServiceAwardReason(Document):
    def validate(self):
        self.validate_expressions()

    def validate_expressions(self):
        """Reject a condition or formula that is not a single Python expression.

        Catching it here means a broken expression fails on the reason that owns
        it, instead of on every End of Service Award that later selects it.
        """
        if not self.amount_based_on_formula:
            self.condition = None
            self.formula = None
            return

        self.amount = 0

        # The condition is optional; a reason with none always pays out.
        for fieldname in ("condition", "formula"):
            expression = self.get(fieldname)
            if not expression:
                continue

            try:
                ast.parse(expression, mode="eval")
            except SyntaxError as e:
                frappe.throw(
                    _("{0} is not a valid Python expression: {1}").format(
                        _(self.meta.get_label(fieldname)), e.msg
                    ),
                    title=_("Invalid Expression"),
                )


@frappe.whitelist()
def get_formula_help():
    """Every name a formula may reference.

    Built from the code that evaluates the formula and from the End of Service
    Award's own meta, so adding a field or a context variable updates the help
    without anyone remembering to edit it.
    """
    frappe.has_permission("End of Service Award Reason", throw=True)

    from common.common_customization.doctype.end_of_service_award.end_of_service_award import (
        FORMULA_GLOBALS,
        FORMULA_VARIABLES,
    )

    meta = frappe.get_meta("End of Service Award")

    return {
        "variables": [
            {"name": name, "description": _(description)}
            for name, description in FORMULA_VARIABLES.items()
        ],
        "helpers": sorted(FORMULA_GLOBALS),
        "doc_fields": [
            {
                "fieldname": df.fieldname,
                "label": _(df.label) if df.label else df.fieldname,
                "fieldtype": df.fieldtype,
            }
            for df in meta.fields
            if df.fieldtype not in no_value_fields
        ],
    }


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_reasons_for_company(doctype, txt, searchfield, start, page_len, filters):
    """The reasons on offer to one company.

    A reason with no company is a shared rule and belongs to all of them. That
    has to be an or_filter rather than `company in (x, "")` - an unset Link is
    NULL, and NULL matches nothing in an IN list.
    """
    company = (filters or {}).get("company")

    return frappe.get_all(
        "End of Service Award Reason",
        fields=["name"],
        filters=[[searchfield, "like", f"%{txt}%"]] if txt else [],
        or_filters=[
            ["company", "=", company],
            ["company", "is", "not set"],
        ],
        order_by="name",
        start=start,
        page_length=page_len,
        as_list=True,
    )
