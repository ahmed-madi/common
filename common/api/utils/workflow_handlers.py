"""
Workflow Action Handlers
Provides a clean, extensible system for handling different types of workflow actions.
"""

import frappe
from frappe import _
from frappe.utils import cint


class WorkflowHandler:
    """Base class for workflow action handlers using Strategy Pattern"""

    def can_handle(self, doc, meta, wf, permissions):
        """
        Check if this handler can process the document
        
        Args:
            doc: Frappe document instance
            meta: Document meta information
            wf: Workflow object (can be None)
            permissions: Document permissions dict
            
        Returns:
            bool: True if this handler can process the document
        """
        raise NotImplementedError

    def get_workflow_data(self, doc, meta, wf, permissions, roles):
        """
        Get workflow data for the document
        
        Args:
            doc: Frappe document instance
            meta: Document meta information
            wf: Workflow object
            permissions: Document permissions dict
            roles: User roles list
            
        Returns:
            dict: Workflow data with state_field and actions
        """
        raise NotImplementedError

    def _create_action(self, action_label, action_value, next_state_label, next_state_value):
        """
        Helper to create standardized action structure
        
        Args:
            action_label: Display label for the action
            action_value: Value for the action
            next_state_label: Display label for next state
            next_state_value: Value for next state
            
        Returns:
            dict: Formatted action object
        """
        return {
            "action": {
                "label": _(action_label),
                "value": action_value,
            },
            "next_state": {
                "label": _(next_state_label),
                "value": next_state_value,
            },
        }


class DefaultWorkflowHandler(WorkflowHandler):
    """Handler for Frappe's standard workflow system"""

    def can_handle(self, doc, meta, wf, permissions):
        """Check if document has a standard Frappe workflow"""
        return wf is not None

    def get_workflow_data(self, doc, meta, wf, permissions, roles):
        """Get workflow actions from Frappe workflow transitions"""
        actions = []
        state_field = wf.workflow_state_field
        current_state = doc.get(state_field)
        
        for transition in wf.transitions:
            # Check if transition is valid for current state and user role
            if current_state != transition.state:
                continue
            if transition.allowed not in roles and frappe.session.user != "Administrator":
                continue

            actions.append(
                self._create_action(
                    action_label=transition.action,
                    action_value=transition.action,
                    next_state_label=transition.next_state,
                    next_state_value=transition.next_state,
                )
            )

        return {
            "state_field": state_field,
            "actions": actions,
        }


class StatusBasedWorkflowHandler(WorkflowHandler):
    """Handler for submittable documents with status field"""

    def can_handle(self, doc, meta, wf, permissions):
        """Check if document is submittable with status field"""
        return (
            wf is None
            and cint(meta.is_submittable) == 1
            and hasattr(doc, "status")
        )

    def get_workflow_data(self, doc, meta, wf, permissions, roles):
        """Get workflow actions based on status and docstatus"""
        actions = []
        state_field = "status"

        # Draft state - can approve or reject
        if (
            doc.status == "Open"
            and doc.docstatus == 0
            and cint(permissions.get("submit")) == 1
        ):
            actions.extend([
                self._create_action(
                    action_label="Approve",
                    action_value="Approve",
                    next_state_label="Approved",
                    next_state_value="Approved",
                ),
                self._create_action(
                    action_label="Reject",
                    action_value="Reject",
                    next_state_label="Rejected",
                    next_state_value="Rejected",
                ),
            ])

        # Submitted state - can cancel
        elif doc.docstatus == 1 and cint(permissions.get("cancel")) == 1:
            actions.append(
                self._create_action(
                    action_label="Cancel",
                    action_value="Cancel",
                    next_state_label="Canceled",
                    next_state_value="Canceled",
                )
            )

        return {
            "state_field": state_field,
            "actions": actions,
        }


class DocstatusWorkflowHandler(WorkflowHandler):
    """Handler for submittable documents using docstatus only"""

    def can_handle(self, doc, meta, wf, permissions):
        """Check if document is submittable without status field"""
        return (
            wf is None
            and cint(meta.is_submittable) == 1
            and not hasattr(doc, "status")
        )

    def get_workflow_data(self, doc, meta, wf, permissions, roles):
        """Get workflow actions based on docstatus"""
        actions = []
        state_field = "docstatus"

        # Draft state - can submit
        if doc.docstatus == 0 and cint(permissions.get("submit")) == 1:
            actions.append(
                self._create_action(
                    action_label="Submit",
                    action_value="Submit",
                    next_state_label="Submitted",
                    next_state_value=1,
                )
            )

        # Submitted state - can cancel
        elif doc.docstatus == 1 and cint(permissions.get("cancel")) == 1:
            actions.append(
                self._create_action(
                    action_label="Cancel",
                    action_value="Cancel",
                    next_state_label="Canceled",
                    next_state_value=2,
                )
            )

        return {
            "state_field": state_field,
            "actions": actions,
        }


class NoWorkflowHandler(WorkflowHandler):
    """Fallback handler for documents without workflow"""

    def can_handle(self, doc, meta, wf, permissions):
        """Always returns True as fallback handler"""
        return True

    def get_workflow_data(self, doc, meta, wf, permissions, roles):
        """Return empty workflow data"""
        return {
            "state_field": None,
            "actions": [],
        }


class WorkflowActionManager:
    """
    Manager class that coordinates workflow handlers
    Uses chain of responsibility pattern to find appropriate handler
    """

    def __init__(self):
        """Initialize with all available handlers in priority order"""
        self.handlers = [
            DefaultWorkflowHandler(),
            StatusBasedWorkflowHandler(),
            DocstatusWorkflowHandler(),
            NoWorkflowHandler(),  # Fallback handler (always last)
        ]

    def get_workflow_data(self, doc, meta, wf, permissions, roles):
        """
        Get workflow data using appropriate handler
        
        Args:
            doc: Frappe document instance
            meta: Document meta information
            wf: Workflow object (can be None)
            permissions: Document permissions dict
            roles: User roles list
            
        Returns:
            dict: Workflow data with state_field and actions
        """
        for handler in self.handlers:
            if handler.can_handle(doc, meta, wf, permissions):
                return handler.get_workflow_data(doc, meta, wf, permissions, roles)

        # Should never reach here due to NoWorkflowHandler fallback
        return {
            "state_field": None,
            "actions": [],
        }
