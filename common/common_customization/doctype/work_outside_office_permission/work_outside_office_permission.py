# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import time_diff_in_hours, date_diff, flt


class WorkOutsideOfficePermission(Document):
    def validate(self):
        self.validate_dates()
        self.validate_times()

    def validate_times(self):
        if self.start_time and self.end_time and time_diff_in_hours(self.end_time, self.start_time) < 0:
            frappe.throw(_("End time cannot be before start time"))

    def validate_dates(self):
        if self.from_date and self.to_date and date_diff(self.to_date, self.from_date) < 0:
            frappe.throw(_("To date cannot be before from date"))

    def before_save(self):
        if self.start_time and self.end_time and time_diff_in_hours(self.end_time, self.start_time) > 0:
            self.total_hours = flt(time_diff_in_hours(self.end_time, self.start_time), 2)
        else:
            self.total_hours = flt(0, 2)

        if self.from_date and self.to_date and date_diff(self.to_date, self.from_date) > 0:
            self.total_days = date_diff(self.to_date, self.from_date)
        else:
            self.total_days = flt(0, 2)
