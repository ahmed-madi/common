from common.api.utils.endpoints import document_list, read_doc


def salary_component_list():
    doctype = "Salary Component"
    fields = [
        "name",
        "salary_component",
        "salary_component_abbr",
        "type",
        "statistical_component",
    ]
    return document_list(doctype, fields)


def read_salary_component(name: str):
    doctype = "Salary Component"
    fields = [
        "name",
        "salary_component",
        "salary_component_abbr",
        "type",
        "statistical_component",
    ]
    return read_doc(doctype, name, origin_fields=fields)
