from common.api.utils.endpoints import document_list, read_doc

fields = [
    "name",
    "salary_component",
    "salary_component_abbr",
    "type",
    "statistical_component",
]
doctype = "Salary Component"


def salary_component_list():
    return document_list(
        doctype,
        fields,
        add_perms=False,
        add_wf=False,
    )


def read_salary_component(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
