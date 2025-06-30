# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_seconds, nowtime
from common.models.base_hr_document import BaseHRDocument
from common.utils import get_combine_datetime

class TaskTimesheetLog(BaseHRDocument):
    def validate(self):
        super().validate()
        self.validate_times()
    
    def validate_times(self):
        total_hours = flt(self.total_hours)
        if self.start_time and self.end_time:
            diff = time_diff_in_seconds(self.end_time, self.start_time)
            if diff <= 0:
                frappe.throw(_("End time can not be before start time"))
            else:
                total_hours = diff / 3600
        self.total_hours = total_hours
        if self.total_hours <= 0:
            frappe.throw(_("Total hours must be greater than zero"))
        

    def _get_missing_mandatory_fields(self):
        missing = super()._get_missing_mandatory_fields()
        if flt(self.total_hours) == 0:
            df = self.meta.get("fields", {"fieldname": ("=", "start_time")})[0]
            if self.get(df.fieldname) in (None, []) or not self.has_content(df):
                missing.append((df.fieldname, self.get_msg(df)))
            df = self.meta.get("fields", {"fieldname": ("=", "end_time")})[0]
            if self.get(df.fieldname) in (None, []) or not self.has_content(df):
                missing.append((df.fieldname, self.get_msg(df)))

        return missing

    def on_submit(self):
        self.create_timehseet()
    
    def create_timehseet(self):
        timesheet =frappe.new_doc("Timesheet")
        timesheet.update({
            "employee": self.employee,
            "posting_date": self.posting_date,
        })
        from_time = get_combine_datetime(self.posting_date, nowtime())
        if self.start_time and self.end_time:
            from_time = get_combine_datetime(self.posting_date, self.start_time)
        
        timesheet.append("time_logs", {
            "from_time": from_time,
            "hours": self.total_hours,
            "project": self.project,
            "task": self.task,
        })
        timesheet.flags.ignore_permissions=True
        timesheet.save()

    
