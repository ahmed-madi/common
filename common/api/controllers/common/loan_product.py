from common.api.utils.resource import BaseResource

class LoanProductResource(BaseResource):
    doctype = "Loan Product"
    fields = ["name", "product_name", "is_term_loan"]
    list_user_filters = [["disabled", "=", 0]]
    list_force_user_filters = True
