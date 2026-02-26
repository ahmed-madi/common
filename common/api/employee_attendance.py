import frappe
from frappe import _
from frappe.utils import getdate, get_first_day, get_last_day, nowdate


@frappe.whitelist()
def get_attendance_data(employee):
    if not employee:
        frappe.throw(_("Employee is required"))

    today = getdate(nowdate())
    start_date = get_first_day(today)
    end_date = get_last_day(today)

    # Fetch Attendance Records
    attendance = frappe.get_all(
        "Attendance",
        filters={
            "employee": employee,
            "attendance_date": ["between", [start_date, end_date]],
            "docstatus": ["<", 2],
        },
        fields=["attendance_date", "status", "leave_type"],
    )

    # Fetch Employee Checkins
    checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]],
            "docstatus": ["<", 2],
        },
        fields=["time", "log_type"],
        order_by="time asc",
    )

    # Fetch Holidays
    holiday_list = frappe.db.get_value("Employee", employee, "holiday_list")
    if not holiday_list:
        holiday_list = frappe.db.get_value(
            "Company",
            frappe.get_cached_value("Employee", employee, "company"),
            "default_holiday_list",
        )

    holidays = []
    if holiday_list:
        holidays = frappe.get_all(
            "Holiday",
            filters={
                "parent": holiday_list,
                "holiday_date": ["between", [start_date, end_date]],
            },
            fields=["holiday_date", "description"],
        )
    return {
        "attendance": attendance,
        "checkins": checkins,
        "holidays": [h.holiday_date for h in holidays],
        "month_name": today.strftime("%B %Y"),
        "start_date": start_date,
        "end_date": end_date,
    }
