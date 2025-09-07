from werkzeug.routing import Rule
from common.api.controllers.hr_requests.salary_identification_letter import (
    salary_identification_letter_list,
    create_salary_identification_letter,
    read_salary_identification_letter,
    update_salary_identification_letter,
    delete_salary_identification_letter,
)

salary_identification_letter_rules = [
    Rule(
        "/hr-requests/salary-identification-letter",
        methods=["GET"],
        endpoint=salary_identification_letter_list,
    ),
    Rule(
        "/hr-requests/salary-identification-letter",
        methods=["POST"],
        endpoint=create_salary_identification_letter,
    ),
    Rule(
        "/hr-requests/salary-identification-letter/<path:name>/",
        methods=["GET"],
        endpoint=read_salary_identification_letter,
    ),
    Rule(
        "/hr-requests/salary-identification-letter/<path:name>/",
        methods=["PUT"],
        endpoint=update_salary_identification_letter,
    ),
    Rule(
        "/hr-requests/salary-identification-letter/<path:name>/",
        methods=["DELETE"],
        endpoint=delete_salary_identification_letter,
    ),
]
