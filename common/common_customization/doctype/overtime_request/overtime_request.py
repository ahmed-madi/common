# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OvertimeRequest(Document):
    def validate(self):
        # Auto-calculate HR time details when the document is saved
        self.calculate_hr_time_details()

    def calculate_hr_time_details(self):
        # Your logic to calculate HR time details goes here
        # For example, you can sum up the overtime hours and set it to a field named "total_overtime_hours"
        total_overtime_hours = 0

        for overtime_entry in self.time_logs:
            total_overtime_hours += overtime_entry.hours

        # Set the calculated total back to the main document
        self.total_hours = total_overtime_hours
