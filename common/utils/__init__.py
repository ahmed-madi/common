from pytz import UnknownTimeZoneError, timezone
from frappe.utils import get_time, getdate, get_datetime, format_datetime


def get_combine_datetime(posting_date, posting_time):
    import datetime

    if isinstance(posting_date, str):
        posting_date = getdate(posting_date)

    if isinstance(posting_time, str):
        posting_time = get_time(posting_time)

    if isinstance(posting_time, datetime.timedelta):
        posting_time = (datetime.datetime.min + posting_time).time()

    return datetime.datetime.combine(posting_date, posting_time)

def format_user_time(value, user_tz, system_tz):
    if not value or user_tz == system_tz:
        return value
    try:
        user_tz = timezone(user_tz)
        system_tz = timezone(system_tz)
        dt = get_datetime(value)
        if not dt:
            return value
        dt = system_tz.localize(dt)
        dt = dt.astimezone(user_tz)
        return format_datetime(dt)
    except UnknownTimeZoneError:
        return value
