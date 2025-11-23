from common.api.utils.endpoints import read_doc

doctype = "Company Policy"


def read_company_policy():
    return read_doc(doctype, doctype, add_perms=False, add_wf=False)
