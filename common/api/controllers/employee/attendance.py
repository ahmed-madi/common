from common.api.utils.endpoints import (
    document_list,
    create_doc,
)


def create_checkin():
    doctype = "Employee Checkin"
    return create_doc(doctype)


def check_in_out_list():
    doctype = "Employee Checkin"
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
    return document_list(doctype, fields, add_perms=False, add_wf=False)


def attendance_list():
    doctype = "Attendance"
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
    return document_list(doctype, fields, add_perms=False, add_wf=False)
