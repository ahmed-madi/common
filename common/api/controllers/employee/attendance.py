from common.api.utils.resource import BaseResource

class EmployeeCheckinResource(BaseResource):
    doctype = "Employee Checkin"
    url_prefix = "/employee"
    resource_name = "checkin"
    fields = [
        "name",
        "employee",
        "employee_name",
        "log_type",
        "location_name",
        "shift",
        "time",
        "device_id",
        "attendance",
        "skip_auto_attendance",
        "latitude",
        "longitude",
        "shift_start",
        "shift_end",
        "offshift",
        "shift_actual_start",
        "shift_actual_end",
    ]
    add_perms = False
    add_wf = False

class AttendanceResource(BaseResource):
    doctype = "Attendance"
    url_prefix = "/employee"
    resource_name = "attendance"
    fields = [
        "name",
        "employee",
        "employee_name",
        "working_hours",
        "status",
        "leave_type",
        "leave_application",
        "attendance_date",
        "department",
        "attendance_request",
        "shift",
        "in_time",
        "out_time",
        "late_entry",
        "early_exit",
        "docstatus",
    ]
    add_perms = False
    add_wf = False
