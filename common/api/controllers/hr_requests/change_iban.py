from common.api.utils.resource import BaseResource


class ChangeIBANRequestResource(BaseResource):
    doctype = "Change IBAN Request"
    url_prefix = "/hr-requests"
    resource_name = "change-iban"
    fields = [
        "name",
        "request_date",
        "employee",
        "employee_name",
        "c_bank_name",
        "c_bank_ac_no",
        "c_iban",
        "bank_name",
        "bank_ac_no",
        "iban",
        "reason",
        "status",
    ]
    add_perms = True
    add_wf = True
