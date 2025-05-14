from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

BASE_FIELDS = ["name", "employee", "employee_name", "fixation_reason", "salary_mode", "bank_name", "employee_iban", "remarks", "effective_date", "bank_name", "remarks", "status"]

def salary_fixation_list():
    doctype = "Salary Fixation"
    return document_list(doctype, BASE_FIELDS)

def create_salary_fixation():
    doctype = "Salary Fixation"
    return create_doc(doctype)

def read_salary_fixation(name: str):
    doctype = "Salary Fixation"
    return read_doc(doctype, name, origin_fields=BASE_FIELDS)


def update_salary_fixation(name: str):
    doctype = "Salary Fixation"
    return update_doc(doctype, name)


def delete_salary_fixation(name: str):
    doctype = "Salary Fixation"
    return delete_doc(doctype, name)
