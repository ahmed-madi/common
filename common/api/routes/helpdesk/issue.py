from common.api.controllers.helpdesk.issue import HRIssueTypeResource, HRIssuePriorityResource

ticket_issue_rules = []
ticket_issue_rules += HRIssueTypeResource.get_routes()
ticket_issue_rules += HRIssuePriorityResource.get_routes()
