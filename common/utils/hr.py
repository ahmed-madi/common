import frappe
from frappe.utils import get_system_timezone
from frappe.model.document import Document
from common.utils import format_user_time

class EmployeeFetch(Document):
    def before_insert(self):
        if hasattr(self, "employee"):
            if not self.employee:
                self.employee = frappe.get_value(
                    "Employee", dict(user_id=self.owner), "name"
                )


def get_employee_from_user(user):
    employee_docname = frappe.db.get_value("Employee", {"user_id": user})
    if employee_docname:
        return frappe.get_doc("Employee", employee_docname).as_dict()
    return {}

def get_last_checkin_status(employee):
    last_check_in = frappe.get_all(
        "Employee Checkin",
        filters={"employee": employee},
        fields=["log_type", "time", "device_id"],
        order_by="time desc",
    )
    if len(last_check_in):
        last_check_in = last_check_in[0]
        system_timezone = get_system_timezone()
        user_tz = frappe.db.get_value("User", frappe.session.user, "time_zone") or system_timezone
        time1 = last_check_in["time"]
        print(time1)
        print(system_timezone)
        print(user_tz)
        print(format_user_time(last_check_in["time"], user_tz, system_timezone))
        print(format_user_time(last_check_in["time"], user_tz, system_timezone))
        last_check_in["time"] = format_user_time(last_check_in["time"], user_tz, system_timezone)
    else:
        last_check_in = {}
    
    return last_check_in