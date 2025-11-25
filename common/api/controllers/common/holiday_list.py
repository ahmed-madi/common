from common.api.utils.endpoints import document_list, read_doc

fields = [
    "name",
    "holiday_list_name",
    "from_date",
    "to_date",
    "total_holidays",
    "color",
]
doctype = "Holiday List"


def holiday_list_list():
    return document_list(doctype, fields, add_perms=False, add_wf=False)


def read_holiday_list(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
