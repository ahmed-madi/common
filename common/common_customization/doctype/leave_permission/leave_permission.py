# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
    time_diff_in_hours,
    today,
    get_last_day,
    get_first_day,
    flt,
    cint,
    getdate,
)


class LeavePermission(Document):
    def before_insert(self):

        if (
            self.start_time
            and self.end_time
            and time_diff_in_hours(self.end_time, self.start_time) < 0
        ):
            frappe.throw(_("End time cannot be before start time"))

        if getdate(self.day) < getdate(today()):
            frappe.throw(_("Can't create leave permissions in previous days"))

    def validate(self):

        self.check_leaves_perms_in_selected_date()
        self.check_total_hours_in_month(
            self.employee, self.day, self.name, self.total_hours
        )

    def check_leaves_perms_in_selected_date(self):
        previous = frappe.db.get_all(
            "Leave Permission",
            filters={
                "docstatus": ("!=", 2),
                "employee": self.employee,
                "day": ("=", self.day),
                "name": ("not in", [self.name]),
            },
            limit=1,
        )
        if len(previous) > 0:
            frappe.throw(
                _(f"Leave permission for {self.employee} in {self.day} already exists")
            )
            return

    @frappe.whitelist()
    def check_total_hours_in_month(
        self, employee, day, name, total_hours, xclient=False
    ):
        if flt(total_hours) > 4:
            if not xclient:
                frappe.throw(_("Total permission hours cannot exceed 4 hours."))
                return
            return _("Total permission hours cannot exceed 4 hours.")
        start_of_month = get_first_day(day)
        end_of_month = get_last_day(day)

        total_hours_list = frappe.get_list(
            "Leave Permission",
            fields=["sum(total_hours) as sum"],
            filters=[
                ["employee", "=", employee],
                ["day", ">=", start_of_month],
                ["day", "<=", end_of_month],
                ["name", "!=", name],
                ["docstatus", "=", 1],
            ],
        )
        total = flt(total_hours_list[0].sum) if total_hours_list else 0
        if total + flt(total_hours) > 4:
            if not xclient:
                frappe.throw(
                    _(
                        f"Total permission hours cannot exceed 4 per month. You only have {cint(4-total)} hour(s)."
                    )
                )
                return
            return _(
                f"Total permission hours cannot exceed 4 per month. You only have {cint(4-total)} hour(s)."
            )

    def before_save(self):
        if (
            self.start_time
            and self.end_time
            and time_diff_in_hours(self.end_time, self.start_time) > 0
        ):
            self.total_hours = flt(
                time_diff_in_hours(self.end_time, self.start_time), 2
            )
        else:
            self.total_hours = flt(0, 2)
