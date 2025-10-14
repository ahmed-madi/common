from common.api.utils.endpoints import document_list, read_doc

fields = [
    "name",
    "salary_component",
    "salary_component_abbr",
    "type",
    "statistical_component",
]
def salary_component_list():
    doctype = "Salary Component"
    return document_list(doctype, fields, translate_text=True, tr_field="salary_component")


def read_salary_component(name: str):
    doctype = "Salary Component"
    return read_doc(doctype, name, origin_fields=fields)
