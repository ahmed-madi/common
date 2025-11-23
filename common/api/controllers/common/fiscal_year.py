from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "year_start_date", "year_end_date"]
doctype = "Fiscal Year"


def fiscal_year_list():
    return document_list(
        doctype,
        fields,
        user_filters=[["disabled", "=", 0]],
        force_user_filters=True,
        add_perms=False,
        add_wf=False,
    )


def read_fiscal_year(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
