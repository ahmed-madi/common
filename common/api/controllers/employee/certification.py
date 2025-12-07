from common.api.utils.resource import BaseResource

class EmployeeCertificationResource(BaseResource):
    doctype = "Employee Certification"
    url_prefix = "/employee"
    resource_name = "certification"
    fields = [
        "name",
        "employee",
        "employee_name",
        "certificate_title",
        "issuing_organization",
        "date_of_issue",
        "attachment",
    ]
    # Old code had safe_api but no perms added explicitly in call? 
    # document_list(..., add_perms=False, add_wf=False).
    # BaseResource DEFAULT is add_perms=False, add_wf=False?
    # NO. BaseResource calls `document_list` without args, so it uses defaults.
    # Default of `document_list` is add_perms=True, add_wf=True?
    # Let's check `common/api/utils/endpoints.py` default. I can't check now easily.
    # But usually API defaults to checking perms.
    # The old code explicitly had `add_perms=False`.
    # I should set `add_perms = False` in class to be safe/consistent.
    add_perms = False
    add_wf = False
