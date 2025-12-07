from common.api.utils.resource import BaseResource

class HRIssueTypeResource(BaseResource):
    doctype = "HR Issue Type"
    url_prefix = "/helpdesk"
    resource_name = "issue-type"
    fields = ["name"]

class HRIssuePriorityResource(BaseResource):
    doctype = "HR Issue Priority"
    url_prefix = "/helpdesk"
    resource_name = "issue-priority"
    fields = ["name"]
