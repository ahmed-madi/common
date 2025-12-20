from common.api.utils.resource import BaseResource


class ClubRequestResource(BaseResource):
    doctype = "Club Request"
    url_prefix = "/hr-requests"
    resource_name = "club-request"
    fields = [
        "name",
        "employee",
        "employee_name",
        "request_date",
        "club_name",
        "start_date",
        "end_date",
        "status",
    ]
    add_perms = True
    add_wf = True
