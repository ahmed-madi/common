from werkzeug.routing import Rule
from common.api.controllers.common.loan_product import loan_product_list, read_loan_product

loan_product_rules = [
	Rule("/hr-common/loan-product", methods=["GET"], endpoint=loan_product_list),
	Rule("/hr-common/loan-product/<path:name>/", methods=["GET"], endpoint=read_loan_product),
]