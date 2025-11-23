from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "fixation_reason"]
doctype = "Fixation Reason"


def salary_fixation_reason_list():
    return document_list(
        doctype,
        fields,
        add_perms=False,
        add_wf=False,
    )


def read_salary_fixation_reason(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
