from common.api.utils.endpoints import document_list, read_doc


def holiday_list_list():
    doctype = "Holiday List"
    fields = [
        "name",
        "holiday_list_name",
        "from_date",
        "to_date",
        "total_holidays",
        "color",
    ]
    return document_list(doctype, fields)


def read_holiday_list(name: str):
    doctype = "Holiday List"
    fields = [
        "name",
        "holiday_list_name",
        "from_date",
        "to_date",
        "total_holidays",
        "color",
        "holidays",
    ]
    return read_doc(doctype, name, origin_fields=fields)
