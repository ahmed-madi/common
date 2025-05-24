
from frappe.utils import get_time, getdate

def get_combine_datetime(posting_date, posting_time):
	import datetime

	if isinstance(posting_date, str):
		posting_date = getdate(posting_date)

	if isinstance(posting_time, str):
		posting_time = get_time(posting_time)

	if isinstance(posting_time, datetime.timedelta):
		posting_time = (datetime.datetime.min + posting_time).time()

	return datetime.datetime.combine(posting_date, posting_time)
