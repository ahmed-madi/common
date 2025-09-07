from werkzeug.routing import Rule
from common.api.controllers.common.fiscal_year import fiscal_year_list, read_fiscal_year

fiscal_year_rules = [
    Rule("/hr-common/fiscal-year", methods=["GET"], endpoint=fiscal_year_list),
    Rule(
        "/hr-common/fiscal-year/<path:name>/",
        methods=["GET"],
        endpoint=read_fiscal_year,
    ),
]
