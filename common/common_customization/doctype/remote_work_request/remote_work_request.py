# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
    date_diff,
    flt,
    cint,
    get_year_start,
    add_months,
    add_days,
    nowdate,
    getdate,
)


class RemoteWorkRequest(Document):
    def validate(self):
        self.validate_dates()
        self.validate_total_requests(self.name, self.from_date, self.employee, self.total_days)

    def before_insert(self):
        if getdate(self.from_date) < getdate(nowdate()) and frappe.session.user != "Administrator":
            frappe.throw(_("From date can't be in the past"))

    def validate_dates(self):
        if self.from_date and self.to_date and date_diff(self.to_date, self.from_date) < 0:
            frappe.throw(_("To date cannot be before from date"))

    @frappe.whitelist()
    def validate_total_requests(self, name, from_date, employee, total_days, xclient=False):
        if flt(total_days) > 12:
            if not xclient:
                frappe.throw(_(f"Total request days cannot exceed 12 days."))

            frappe.throw(_(f"Total request days cannot exceed 12 days."))
        start_of_year = get_year_start(from_date)
        end_of_year = add_days(add_months(start_of_year, 11), 30)
        total_request_days = frappe.get_list(
            "Remote Work Request",
            fields=["sum(total_days) as sum"],
            filters={
                "employee": employee,
                "from_date": [">=", start_of_year],
                "to_date": ["<", end_of_year],
                "name": ["!=", name],
                "docstatus": 1,
            },
        )
        total = flt(total_request_days[0].sum) + 1 if total_request_days else 0
        if total + flt(total_days) > 12:
            if not xclient:
                frappe.throw(_(f"Total request days cannot exceed 12 per year. You only have {cint(12-total)} day(s)."))

            frappe.throw(_(f"Total request days cannot exceed 12 per year. You only have {cint(12-total)} day(s)."))

    def before_save(self):
        if self.from_date and self.to_date and date_diff(self.to_date, self.from_date) + 1 > 0:
            self.total_days = date_diff(self.to_date, self.from_date) + 1
        else:
            self.total_days = 0
