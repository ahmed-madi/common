"""
Workflow Action Executors
Handles the execution of workflow actions for different workflow types.
Each executor knows how to perform actions specific to its workflow type.
"""

import frappe
from frappe import _
from frappe.utils import cint


class WorkflowActionExecutor:
    """Base class for workflow action executors"""

    def can_execute(self, doc, meta, action_value):
        """
        Check if this executor can handle the action for this document
        
        Args:
            doc: Frappe document instance
            meta: Document meta information
            action_value: The action value to execute
            
        Returns:
            bool: True if this executor can handle the action
        """
        raise NotImplementedError

    def execute_action(self, doc, action_value, next_state_value):
        """
        Execute the workflow action
        
        Args:
            doc: Frappe document instance
            action_value: The action to execute (e.g., "Submit", "Approve")
            next_state_value: The next state value
            
        Returns:
            dict: Result with success status and message
        """
        raise NotImplementedError


class DefaultWorkflowActionExecutor(WorkflowActionExecutor):
    """Executor for Frappe's standard workflow system"""

    def can_execute(self, doc, meta, action_value):
        """Check if document has a Frappe workflow"""
        workflow_name = frappe.get_value("Workflow", {"document_type": doc.doctype, "is_active": 1}, "name")
        return workflow_name is not None

    def execute_action(self, doc, action_value, next_state_value):
        """
        Execute workflow action using Frappe's workflow system
        This uses the built-in apply_workflow method
        """
        try:
            # Apply the workflow action
            doc.reload()  # Ensure we have latest data
            
            # Use Frappe's built-in workflow application
            from frappe.model.workflow import apply_workflow
            apply_workflow(doc, action_value)
            
            return {
                "success": True,
                "message": _("Workflow action '{0}' applied successfully").format(action_value),
                "doc": doc.as_dict()
            }
            
        except frappe.PermissionError as e:
            frappe.log_error(f"Workflow permission error: {str(e)}")
            return {
                "success": False,
                "message": _("You don't have permission to perform this action"),
                "error": str(e)
            }
        except Exception as e:
            frappe.log_error(f"Workflow action error: {str(e)}")
            return {
                "success": False,
                "message": _("Failed to execute workflow action: {0}").format(str(e)),
                "error": str(e)
            }


class StatusBasedActionExecutor(WorkflowActionExecutor):
    """Executor for status-based workflow (Approve/Reject/Cancel)"""

    def can_execute(self, doc, meta, action_value):
        """Check if document is submittable with status field"""
        return cint(meta.is_submittable) == 1 and hasattr(doc, "status")

    def execute_action(self, doc, action_value, next_state_value):
        """
        Execute status-based action (Approve/Reject/Cancel)
        
        Actions:
        - Approve: Set status to "Approved" and submit document
        - Reject: Set status to "Rejected" and submit document
        - Cancel: Cancel the submitted document
        """
        try:
            doc.reload()  # Ensure we have latest data
            
            if action_value == "Approve":
                # Set status and submit
                doc.status = "Approved"
                doc.save()
                doc.submit()
                message = _("Document approved and submitted successfully")
                
            elif action_value == "Reject":
                # Set status and submit (as rejected)
                doc.status = "Rejected"
                doc.save()
                doc.submit()
                message = _("Document rejected successfully")
                
            elif action_value == "Cancel":
                # Cancel the document
                doc.cancel()
                doc.status = "Canceled"
                doc.save()
                message = _("Document canceled successfully")
                
            else:
                return {
                    "success": False,
                    "message": _("Unknown action: {0}").format(action_value)
                }
            
            return {
                "success": True,
                "message": message,
                "doc": doc.as_dict()
            }
            
        except frappe.PermissionError as e:
            frappe.log_error(f"Permission error: {str(e)}")
            return {
                "success": False,
                "message": _("You don't have permission to perform this action"),
                "error": str(e)
            }
        except Exception as e:
            frappe.log_error(f"Status action error: {str(e)}")
            return {
                "success": False,
                "message": _("Failed to execute action: {0}").format(str(e)),
                "error": str(e)
            }


class DocstatusActionExecutor(WorkflowActionExecutor):
    """Executor for docstatus-only workflow (Submit/Cancel)"""

    def can_execute(self, doc, meta, action_value):
        """Check if document is submittable without status field"""
        return cint(meta.is_submittable) == 1 and not hasattr(doc, "status")

    def execute_action(self, doc, action_value, next_state_value):
        """
        Execute docstatus action (Submit/Cancel)
        
        Actions:
        - Submit: Submit the document (docstatus = 1)
        - Cancel: Cancel the document (docstatus = 2)
        """
        try:
            doc.reload()  # Ensure we have latest data
            
            if action_value == "Submit":
                # Submit the document
                doc.submit()
                message = _("Document submitted successfully")
                
            elif action_value == "Cancel":
                # Cancel the document
                doc.cancel()
                message = _("Document canceled successfully")
                
            else:
                return {
                    "success": False,
                    "message": _("Unknown action: {0}").format(action_value)
                }
            
            return {
                "success": True,
                "message": message,
                "doc": doc.as_dict()
            }
            
        except frappe.PermissionError as e:
            frappe.log_error(f"Permission error: {str(e)}")
            return {
                "success": False,
                "message": _("You don't have permission to perform this action"),
                "error": str(e)
            }
        except Exception as e:
            frappe.log_error(f"Docstatus action error: {str(e)}")
            return {
                "success": False,
                "message": _("Failed to execute action: {0}").format(str(e)),
                "error": str(e)
            }


class WorkflowActionExecutionManager:
    """
    Manager class that coordinates workflow action executors
    Uses chain of responsibility pattern to find appropriate executor
    """

    def __init__(self):
        """Initialize with all available executors in priority order"""
        self.executors = [
            DefaultWorkflowActionExecutor(),
            StatusBasedActionExecutor(),
            DocstatusActionExecutor(),
        ]

    def execute_workflow_action(self, doctype, docname, action_value, next_state_value=None):
        """
        Execute a workflow action on a document
        
        Args:
            doctype: Document type
            docname: Document name
            action_value: Action to execute (e.g., "Submit", "Approve", "Reject")
            next_state_value: Optional next state value
            
        Returns:
            dict: Result with success status, message, and updated document
        """
        try:
            # Get the document
            doc = frappe.get_doc(doctype, docname)
            meta = frappe.get_meta(doctype)
            
            # Check permissions
            if not doc.has_permission("write"):
                return {
                    "success": False,
                    "message": _("You don't have permission to modify this document")
                }
            
            # Find appropriate executor
            for executor in self.executors:
                if executor.can_execute(doc, meta, action_value):
                    result = executor.execute_action(doc, action_value, next_state_value)
                    
                    # Commit if successful
                    if result.get("success"):
                        frappe.db.commit()
                    
                    return result
            
            # No executor found
            return {
                "success": False,
                "message": _("No executor found for this action")
            }
            
        except frappe.DoesNotExistError:
            return {
                "success": False,
                "message": _("Document not found: {0}").format(docname)
            }
        except Exception as e:
            frappe.log_error(f"Workflow execution error: {str(e)}")
            frappe.db.rollback()
            return {
                "success": False,
                "message": _("Failed to execute workflow action: {0}").format(str(e)),
                "error": str(e)
            }
