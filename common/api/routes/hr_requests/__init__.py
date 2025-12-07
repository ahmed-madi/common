from common.api.controllers.hr_requests.unified import UnifiedRequestResource, UnifiedRequestStatusResource

employee_requests_rules = []
employee_requests_rules += UnifiedRequestResource.get_routes()
employee_requests_rules += UnifiedRequestStatusResource.get_routes()
