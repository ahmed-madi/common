import frappe
from frappe.utils import getdate, get_first_day, get_last_day, add_days, flt


@frappe.whitelist()
def get_attendance_summary(year, month, search=None, start=0, page_length=20):
    actual_year = year
    if year and "-" in str(year):
        actual_year = str(year).split("-")[0]

    try:
        actual_year = int(actual_year)
    except (ValueError, TypeError):
        actual_year = getdate().year

    month = int(month)
    start = int(start)
    page_length = int(page_length)

    start_date = get_first_day(getdate(f"{actual_year}-{month}-01"))
    end_date = get_last_day(start_date)
    days_in_month = (end_date - start_date).days + 1

    filters = [["status", "=", "Active"]]
    or_filters = []
    if search:
        or_filters.append(
            ["name", "like", f"%{search}%"],
        )
        or_filters.append(
            ["employee_name", "like", f"%{search}%"],
        )

    # Get total count for pagination
    total_count = len(
        frappe.get_all("Employee", filters=filters, or_filters=or_filters)
    )

    employees = frappe.get_all(
        "Employee",
        filters=filters,
        or_filters=or_filters,
        fields=["name", "employee_name", "designation", "image"],
        order_by="employee_name asc",
        limit_start=start,
        limit_page_length=page_length,
    )

    attendance_data = frappe.get_all(
        "Attendance",
        filters={
            "attendance_date": ["between", [start_date, end_date]],
            "docstatus": ["<", 2],
        },
        fields=[
            "employee",
            "attendance_date",
            "status",
            "working_hours",
            "late_entry",
            "early_exit",
        ],
    )

    # Organize attendance by employee
    attendance_map = {}
    for d in attendance_data:
        if d.employee not in attendance_map:
            attendance_map[d.employee] = {}
        attendance_map[d.employee][d.attendance_date] = d

    # Fetch Checkins for missing fingerprint detection
    checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "time": ["between", [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]],
            "docstatus": ["<", 2],
        },
        fields=["employee", "time", "log_type"],
    )

    checkin_map = {}
    for c in checkins:
        date = getdate(c.time)
        if c.employee not in checkin_map:
            checkin_map[c.employee] = {}
        if date not in checkin_map[c.employee]:
            checkin_map[c.employee][date] = []
        checkin_map[c.employee][date].append(c)

    # Fetch Holidays
    holiday_lists = frappe.get_all("Holiday List", fields=["name"])
    holidays_by_list = {}
    for hl in holiday_lists:
        res = frappe.get_all(
            "Holiday",
            filters={
                "parent": hl.name,
                "holiday_date": ["between", [start_date, end_date]],
            },
            fields=["holiday_date"],
        )
        holidays_by_list[hl.name] = [h.holiday_date for h in res]

    result = []

    for emp in employees:
        emp_attendance = attendance_map.get(emp.name, {})
        emp_checkins = checkin_map.get(emp.name, {})

        holiday_list = frappe.db.get_value("Employee", emp.name, "holiday_list")
        if not holiday_list:
            company = frappe.get_cached_value("Employee", emp.name, "company")
            holiday_list = frappe.db.get_value(
                "Company", company, "default_holiday_list"
            )

        emp_holidays = holidays_by_list.get(holiday_list, [])

        actual_hours = 0
        scheduled_hours = 0  # Simplified: Assuming 8h per working day for now
        late_count = 0
        early_exit_count = 0
        missing_fingerprint = 0

        daily_status = []

        for i in range(days_in_month):
            curr_date = add_days(start_date, i)
            status_info = emp_attendance.get(curr_date)

            is_holiday = curr_date in emp_holidays
            is_weekend = curr_date.weekday() in [
                4,
                5,
            ]  # Assuming Fri/Sat as weekend for the region

            day_status = "absent"
            if is_holiday or is_weekend:
                day_status = "holiday"
            else:
                scheduled_hours += 8

            if status_info:
                if status_info.status == "Present":
                    day_status = "present"
                    actual_hours += flt(status_info.working_hours)
                    if status_info.late_entry:
                        late_count += 1
                    if status_info.early_exit:
                        early_exit_count += 1
                elif status_info.status in ["On Leave", "Half Day"]:
                    day_status = "leave"

            # Missing fingerprint logic (if no status or present but incomplete checkins)
            if not is_holiday and not is_weekend:
                day_checkins = emp_checkins.get(curr_date, [])
                if len(day_checkins) % 2 != 0:
                    missing_fingerprint += 1

            daily_status.append({"date": curr_date, "status": day_status})

        result.append(
            {
                "employee": emp.name,
                "employee_name": emp.employee_name,
                "designation": emp.designation,
                "image": emp.image,
                "scheduled_hours": scheduled_hours,
                "actual_hours": actual_hours,
                "difference": actual_hours - scheduled_hours,
                "late_count": late_count,
                "early_exit_count": early_exit_count,
                "missing_fingerprint": missing_fingerprint,
                "daily_status": daily_status,
            }
        )

    return {
        "employees": result,
        "days": days_in_month,
        "start_date": start_date,
        "total_count": total_count,
    }
