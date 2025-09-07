from common.api.utils.endpoints import read_doc


def read_company_policy():
    doctype = "Company Policy"
    fields = ["*"]
    return read_doc(doctype, doctype, origin_fields=fields)
