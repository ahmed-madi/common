
from common.api.utils.endpoints import document_list, create_doc, read_doc, update_doc ,delete_doc

def salary_identification_letter_list():
    doctype = "Salary Identification Letter"
    fields = ["*"]
    return document_list(doctype, fields)

def create_salary_identification_letter():
    doctype = "Salary Identification Letter"
    return create_doc(doctype)

def read_salary_identification_letter(name: str):
    doctype = "Salary Identification Letter"    
    return read_doc(doctype, name)


def update_salary_identification_letter(name: str):
    doctype = "Salary Identification Letter"
    return update_doc(doctype, name)


def delete_salary_identification_letter(name: str):
    doctype = "Salary Identification Letter"
    return delete_doc(doctype, name)

