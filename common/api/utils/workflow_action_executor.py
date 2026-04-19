"""
Workflow Action Execution Manager for Frappe v15.

apply_workflow() in frappe.model.workflow handles all docstatus transitions
internally (draft→draft saves, draft→submitted submits, submitted→cancelled cancels)
based on each workflow state's doc_status setting. We delegate entirely to it.

For submittable doctypes that have no active workflow, direct submit/cancel is used.
"""

import frappe
from frappe import _
from frappe.utils import cint


class WorkflowActionExecutionManager:
    """
    Executes workflow actions for a given document.

    Two paths:
      1. Active workflow exists  → delegate to frappe.model.workflow.apply_workflow
      2. No workflow, submittable → direct doc.submit() / doc.cancel()
    """

    def execute_workflow_action(self, doctype, docname, action_value, next_state_value=None):
        try:
            doc = frappe.get_doc(doctype, docname)
            meta = frappe.get_meta(doctype)
        except frappe.DoesNotExistError:
            return {
                "success": False,
                "message": _("{0} '{1}' does not exist").format(doctype, docname),
            }

        if not doc.has_permission("write"):
            return {
                "success": False,
                "message": _("You don't have permission to modify this document"),
            }

        workflow_name = frappe.get_value(
            "Workflow", {"document_type": doctype, "is_active": 1}, "name"
        )

        if workflow_name:
            return self._apply_workflow(doc, action_value)

        if cint(meta.is_submittable):
            return self._direct_action(doc, action_value)

        return {
            "success": False,
            "message": _("No active workflow or submit action available for {0}").format(doctype),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_workflow(self, doc, action_value):
        """Delegate to Frappe's apply_workflow which manages all docstatus transitions."""
        from frappe.model.workflow import (
            WorkflowPermissionError,
            WorkflowStateError,
            WorkflowTransitionError,
            apply_workflow,
        )

        try:
            result_doc = apply_workflow(doc, action_value)

            # apply_workflow returns None when the submission is queued in background
            if result_doc is None:
                frappe.db.commit()
                return {
                    "success": True,
                    "queued": True,
                    "message": _("Action '{0}' queued for background processing").format(action_value),
                }

            frappe.db.commit()
            return {
                "success": True,
                "message": _("Workflow action '{0}' applied successfully").format(action_value),
                "doc": result_doc.as_dict(),
            }

        except WorkflowTransitionError as e:
            frappe.db.rollback()
            return {
                "success": False,
                "message": str(e) or _("Action '{0}' is not available in the current workflow state").format(action_value),
                "error": str(e),
            }
        except WorkflowStateError as e:
            frappe.db.rollback()
            return {
                "success": False,
                "message": str(e) or _("Workflow state is not set on this document"),
                "error": str(e),
            }
        except WorkflowPermissionError as e:
            frappe.db.rollback()
            return {
                "success": False,
                "message": str(e) or _("You are not permitted to perform this workflow action"),
                "error": str(e),
            }
        except frappe.PermissionError as e:
            frappe.db.rollback()
            return {
                "success": False,
                "message": _("You don't have permission to perform this action"),
                "error": str(e),
            }
        except frappe.ValidationError as e:
            frappe.log_error(title="Workflow Action Validation Error", message=frappe.get_traceback())
            frappe.db.rollback()
            return {
                "success": False,
                "message": str(e) or _("Workflow action '{0}' failed validation").format(action_value),
                "error": str(e),
            }
        except Exception as e:
            frappe.log_error(title="Workflow Action Error", message=frappe.get_traceback())
            frappe.db.rollback()
            return {
                "success": False,
                "message": _("Failed to apply workflow action '{0}': {1}").format(action_value, str(e)),
                "error": str(e),
            }

    def _direct_action(self, doc, action_value):
        """Submit or cancel a submittable doc that has no active workflow."""
        try:
            doc.reload()

            if action_value == "Submit":
                doc.submit()
                message = _("Document submitted successfully")
            elif action_value == "Cancel":
                doc.cancel()
                message = _("Document canceled successfully")
            else:
                return {
                    "success": False,
                    "message": _("Action '{0}' is not supported without an active workflow").format(action_value),
                }

            frappe.db.commit()
            return {
                "success": True,
                "message": message,
                "doc": doc.as_dict(),
            }

        except frappe.PermissionError as e:
            frappe.db.rollback()
            return {
                "success": False,
                "message": _("You don't have permission to perform this action"),
                "error": str(e),
            }
        except frappe.ValidationError as e:
            frappe.log_error(title="Direct Action Validation Error", message=frappe.get_traceback())
            frappe.db.rollback()
            return {
                "success": False,
                "message": str(e) or _("Action '{0}' failed validation").format(action_value),
                "error": str(e),
            }
        except Exception as e:
            frappe.log_error(title="Direct Action Error", message=frappe.get_traceback())
            frappe.db.rollback()
            return {
                "success": False,
                "message": _("Failed to execute action '{0}': {1}").format(action_value, str(e)),
                "error": str(e),
            }
