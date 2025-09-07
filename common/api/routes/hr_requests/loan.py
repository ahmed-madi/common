from werkzeug.routing import Rule
from common.api.controllers.hr_requests.loan import (
    loan_list,
    create_loan,
    read_loan,
    update_loan,
    delete_loan,
)

loan_rules = [
    Rule("/hr-requests/loan", methods=["GET"], endpoint=loan_list),
    Rule("/hr-requests/loan", methods=["POST"], endpoint=create_loan),
    Rule("/hr-requests/loan/<path:name>/", methods=["GET"], endpoint=read_loan),
    Rule("/hr-requests/loan/<path:name>/", methods=["PUT"], endpoint=update_loan),
    Rule("/hr-requests/loan/<path:name>/", methods=["DELETE"], endpoint=delete_loan),
]
