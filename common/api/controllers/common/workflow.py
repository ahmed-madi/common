import frappe
from frappe import _
from common.api.utils.resource import BaseResource
from common.api.utils.decorators import safe_api
from common.api.utils.workflow_action_executor import WorkflowActionExecutionManager
from common.api.utils.endpoints import get_doc
from common.api.utils import get_request_form_data
from werkzeug.routing import Rule


class WorkflowActionResource(BaseResource):
    doctype = "Workflow Action"
    url_prefix = "/common"
    resource_name = "workflow-action"

    @classmethod
    def execute(cls):
        @safe_api
        def _execute():
            # Extract request data
            data = get_request_form_data()

            # Get parameters from request body
            doctype = data.get("doctype")
            docname = data.get("docname")
            action = data.get("action")
            next_state = data.get("next_state")

            # Validate inputs
            if not doctype or not docname or not action:
                from frappe import ValidationError

                raise ValidationError(_("doctype, docname, and action are required"))
            # Execute the action
            manager = WorkflowActionExecutionManager()
            result = manager.execute_workflow_action(
                doctype=doctype,
                docname=docname,
                action_value=action,
                next_state_value=next_state,
            )

            if not result.get("success"):
                from frappe import ValidationError

                raise ValidationError(result.get("message", _("Unknown error")))

            # Get updated document with permissions and workflow
            updated_doc = get_doc(
                doctype=doctype, name=docname, add_perms=True, add_wf=True
            )

            return updated_doc, result.get("message")

        _execute.__name__ = "execute_workflow_action"
        return _execute

    @classmethod
    def get_routes(cls):
        return [
            Rule("/hr-common/workflow-action", methods=["POST"], endpoint=cls.execute())
        ]


@frappe.whitelist()
def execute_workflow_action():
    return WorkflowActionResource.execute()()
