from common.api.utils.endpoints import document_list, read_doc

BASE_FIELDS = ["name", "disabled", "year_start_date", "year_end_date"]


def fiscal_year_list():
    doctype = "Fiscal Year"
    return document_list(doctype, BASE_FIELDS)


def read_fiscal_year(name: str):
    doctype = "Fiscal Year"
    return read_doc(doctype, name, origin_fields=BASE_FIELDS)
