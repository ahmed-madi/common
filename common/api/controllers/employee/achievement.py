from common.api.utils.resource import BaseResource


class EmployeeAchievementResource(BaseResource):
    doctype = "Employee Achievement"
    url_prefix = "/employee"
    resource_name = "achievement"
    fields = [
        "name",
        "employee",
        "employee_name",
        "title",
        "date",
        "description",
        "attachment",
    ]
