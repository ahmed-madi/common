from common.api.utils.resource import BaseResource

class LoanApplicationResource(BaseResource):
    doctype = "Loan Application"
    url_prefix = "/hr-requests"
    resource_name = "loan"
    fields = ["name", "applicant", "applicant_name", "posting_date", "loan_product", "status"]
    add_perms = True
    add_wf = True
