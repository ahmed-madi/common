from werkzeug.routing import Rule
from common.api.controllers.common.company_policy import read_company_policy

company_policy_rules = [
    Rule("/hr-common/company-policy", methods=["GET"], endpoint=read_company_policy),
]
