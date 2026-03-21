from common.api.controllers.hr_requests.unified import (
    UnifiedRequestResource,
    UnifiedRequestStatusResource,
)
from common.api.controllers.hr_requests.unified_hr_support import (
    HRSupportResource,
    HRSupportStatusResource,
)

employee_requests_rules = []
employee_requests_rules += UnifiedRequestResource.get_routes()
employee_requests_rules += UnifiedRequestStatusResource.get_routes()
employee_requests_rules += HRSupportResource.get_routes()
employee_requests_rules += HRSupportStatusResource.get_routes()
