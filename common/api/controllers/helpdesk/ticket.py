from common.api.utils.resource import BaseResource


class HRTicketResource(BaseResource):
    doctype = "HR Ticket"
    url_prefix = "/helpdesk"
    resource_name = "ticket"
    fields = ["name", "subject", "status", "opening_date", "opening_time", "department"]
    add_perms = True
    add_wf = True
