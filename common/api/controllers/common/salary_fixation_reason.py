from common.api.utils.endpoints import document_list, read_doc


def salary_fixation_reason_list():
    doctype = "Fixation Reason"
    fields = ["name", "fixation_reason"]
    return document_list(
        doctype, fields, translate_text=True, tr_field="fixation_reason"
    )


def read_salary_fixation_reason(name: str):
    doctype = "Fixation Reason"
    fields = ["name", "fixation_reason"]
    return read_doc(doctype, name, origin_fields=fields)
