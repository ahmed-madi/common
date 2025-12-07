from common.api.utils.resource import BaseResource

class LeaveApplicationResource(BaseResource):
    doctype = "Leave Application"
    url_prefix = "/leave-requests"
    resource_name = "leave-application"
    fields = [
        "name", 
        "employee", 
        "employee_name", 
        "leave_type", 
        "from_date", 
        "to_date", 
        "total_leave_days", 
        "status"
    ]
    add_perms = True
    add_wf = True
