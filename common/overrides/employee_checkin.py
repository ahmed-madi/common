import frappe
from frappe.utils import getdate
from hrms.hr.doctype.employee_checkin.employee_checkin import (
    EmployeeCheckin as BaseEmployeeCheckin,
)


class EmployeeCheckin(BaseEmployeeCheckin):
    def validate_distance_from_shift_location(self):
        if self.skip_validate_distance():
            return
        super().validate_distance_from_shift_location()

    def skip_validate_distance(self):
        date = getdate(self.time)
        # Work From Home Request
        return frappe.db.exists(
            "Work From Home Request",
            {
                "employee": self.employee,
                "from_date": ["<=", date],
                "to_date": [">=", date],
                "status": "Approved",
                "docstatus": 1,
            },
        )
