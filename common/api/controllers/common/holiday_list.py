from common.api.utils.endpoints import document_list, read_doc

fields = [
    "name",
    "holiday_list_name",
    "from_date",
    "to_date",
    "total_holidays",
    "color",
]


def holiday_list_list():
    doctype = "Holiday List"
    return document_list(
        doctype, fields, translate_text=True, tr_field="holiday_list_name"
    )


def read_holiday_list(name: str):
    doctype = "Holiday List"
    return read_doc(doctype, name, origin_fields=fields)
