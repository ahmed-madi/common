from common.api.utils.resource import BaseResource

class SalaryIdentificationLetterResource(BaseResource):
    doctype = "Salary Identification Letter"
    url_prefix = "/hr-requests"
    resource_name = "salary-identification-letter"
    fields = ["name", "employee", "employee_name", "request_date", "recipient_name", "preferred_language", "signed_pdf_document", "status"]
    add_perms = True
    add_wf = True
