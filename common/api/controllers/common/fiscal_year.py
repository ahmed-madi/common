from common.api.utils.resource import BaseResource

class FiscalYearResource(BaseResource):
    doctype = "Fiscal Year"
    fields = ["name", "year_start_date", "year_end_date"]
    
    list_user_filters = [["disabled", "=", 0]]
    list_force_user_filters = True
