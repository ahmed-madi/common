from common.api.utils.resource import BaseResource

class HolidayListResource(BaseResource):
    doctype = "Holiday List"
    fields = [
        "name",
        "holiday_list_name",
        "from_date",
        "to_date",
        "total_holidays",
        "color",
    ]
