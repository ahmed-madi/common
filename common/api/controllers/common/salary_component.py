from common.api.utils.resource import BaseResource

class SalaryComponentResource(BaseResource):
    doctype = "Salary Component"
    fields = [
        "name",
        "salary_component",
        "salary_component_abbr",
        "type",
        "statistical_component",
    ]
