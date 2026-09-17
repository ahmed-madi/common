# Copyright (c) 2026, Ahmed Madi and contributors
# For license information, please see license.txt

import ast

import frappe
from frappe import _
from frappe.model import no_value_fields
from frappe.model.document import Document


class EndofServiceAwardReason(Document):
    def validate(self):
        self.validate_formula()

    def validate_formula(self):
        """Reject a formula that is not a single Python expression.

        Catching it here means a broken formula fails on the reason that owns
        it, instead of on every End of Service Award that later selects it.
        """
        if not self.amount_based_on_formula:
            self.formula = None
            return

        self.amount = 0

        try:
            ast.parse(self.formula, mode="eval")
        except SyntaxError as e:
            frappe.throw(
                _("Formula is not a valid Python expression: {0}").format(e.msg),
                title=_("Invalid Formula"),
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
