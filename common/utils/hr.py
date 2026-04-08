from datetime import datetime

import frappe
from frappe.utils import get_system_timezone, now_datetime
from frappe.model.document import Document

from hrms.hr.doctype.shift_assignment.shift_assignment import (
    get_shifts_for_date,
    get_shift_details,
    get_prev_or_next_shift,
    _adjust_overlapping_shifts,
    _is_shift_outside_assignment_period,
)

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
        user_tz = (
            frappe.db.get_value("User", frappe.session.user, "time_zone")
            or system_timezone
        )

        last_check_in["time"] = format_user_time(
            last_check_in["time"], user_tz, system_timezone
        )
    else:
        last_check_in = {}

    return last_check_in

def get_employee_shift(
    employee: str,
    for_timestamp: datetime | None = None,
    consider_default_shift: bool = False,
    next_shift_direction: str | None = None,
) -> dict:
    """Returns a Shift Type for the given employee on the given date

    :param employee: Employee for which shift is required.
    :param for_timestamp: DateTime on which shift is required
    :param consider_default_shift: If set to true, default shift is taken when no shift assignment is found.
    :param next_shift_direction: One of: None, 'forward', 'reverse'. Direction to look for next shift if shift not found on given date.
    """
    if for_timestamp is None:
        for_timestamp = now_datetime()

    shift_details = get_shift_for_timestamp(employee, for_timestamp)

    # if shift assignment is not found, consider default shift
    default_shift = frappe.db.get_value("Employee", employee, "default_shift", cache=True)
    if not shift_details and consider_default_shift:
        shift_details = get_shift_details(default_shift, for_timestamp)

    # if no shift is found, find next or prev shift assignment based on direction
    if not shift_details and next_shift_direction:
        shift_details = get_prev_or_next_shift(
            employee, for_timestamp, consider_default_shift, default_shift, next_shift_direction
        )

    return shift_details or {}

def get_shift_for_timestamp(employee: str, for_timestamp: datetime) -> dict:
    shifts = get_shifts_for_date(employee, for_timestamp)
    if shifts:
        return get_shift_for_time(shifts, for_timestamp)
    return {}

def get_shift_for_time(shifts: list[dict], for_timestamp: datetime) -> dict:
    """Returns shift with details for given timestamp"""
    valid_shifts = []

    for assignment in shifts:
        shift_details = get_shift_details(assignment.shift_type, for_timestamp=for_timestamp)

        if _is_shift_outside_assignment_period(shift_details, assignment):
            continue

        valid_shifts.append(shift_details)

    valid_shifts.sort(key=lambda x: x["actual_start"])
    _adjust_overlapping_shifts(valid_shifts)

    return get_exact_shift(valid_shifts, for_timestamp)

def get_exact_shift(shifts: list, for_timestamp: datetime) -> dict:
	"""Returns the shift details (dict) for the exact shift in which the 'for_timestamp' value falls among multiple shifts"""

	return next(
		(
			shift
			for shift in shifts
		),
		{},
	)
