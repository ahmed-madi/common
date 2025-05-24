from werkzeug.routing import Rule
from common.api.controllers.helpdesk.issue import issue_priority_list, issue_type_list

ticket_issue_rules = [
	Rule("/helpdesk/issue-type", methods=["GET"], endpoint=issue_type_list),
	Rule("/helpdesk/issue-priority", methods=["GET"], endpoint=issue_priority_list),
]