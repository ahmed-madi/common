import frappe
from frappe.utils import today


def is_half_holiday(holiday_list, date=None):
    """Returns true if the given date is a half holiday in the given holiday list"""
    if date is None:
        date = today()
    if holiday_list:
        return bool(
            frappe.db.exists(
                "Holiday",
                {"parent": holiday_list, "holiday_date": date, "is_half_day": 1},
                cache=True,
            )
        )
    else:
        return False


def patch_holiday_list():
    import erpnext.setup.doctype.holiday_list.holiday_list

    erpnext.setup.doctype.holiday_list.holiday_list.is_half_holiday = is_half_holiday
