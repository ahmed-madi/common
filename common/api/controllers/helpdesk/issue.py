from common.api.utils.endpoints import document_list


def issue_type_list():
    doctype = "HR Issue Type"
    fields = ["name"]
    return document_list(doctype, fields, add_perms=False, add_wf=False)


def issue_priority_list():
    doctype = "HR Issue Priority"
    fields = ["name"]
    return document_list(doctype, fields, add_perms=False, add_wf=False)
