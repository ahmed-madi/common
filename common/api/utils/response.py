import frappe
from frappe import _
from erpnext.projects.doctype.timesheet.timesheet import OverlapError
from common.api.utils import delete_duplicated_or_after_error
import time
from typing import Any, List


def build_error_response(status_code, message, error, missing_data=None):
    return build_response(
        status="failed",
        status_code=status_code,
        message=message,
        error=error,
        missing_data=missing_data,
    )


def build_success_response(status_code, message, data, extra_data={}):
    if extra_data:
        data.update(extra_data)
    return build_response(
        status="success", status_code=status_code, message=message, data=data
    )


def build_response(
    status: str = None,
    status_code: int = None,
    data: Any = None,
    error: Any = None,
    message: str = None,
    missing_data: List[str] = None,
):
    """
    Standardized API response builder.
    Injects request_id and timestamp for observability.
    """
    response = {
        "status": status,
        "statusCode": status_code,
        "http_status_code": status_code,
        "data": data,
        "error": error,
        "message": message,
        # Observability fields
        "timestamp": time.time(),
        "request_id": getattr(frappe.local, "request_id", None),
    }

    if missing_data:
        response["missing_data"] = missing_data

    frappe.local.response.update(response)
    
    # Cleanup flags
    frappe.local.message_log = []
    frappe.local.debug_log = None
    frappe.flags.error_message = None


def sanitize_error_message(exception: Exception) -> str:
    """
    Sanitize error message to be user-friendly and secure.
    Removes implementation details and technical jargon.
    """
    if not exception:
        return _("An unknown error occurred")

    if hasattr(exception, "args") and exception.args:
        message = str(exception.args[0])
        
        # Handle specific noisy error messages
        if "Application period cannot be outside" in message:
             return message.split(" , ")[0]
        
        if "Cannot link cancelled document" in message:
            return message
            
        if ". It should be one of " in message:
            return message.replace('"', "'")

        # General sanitization: often errors are "Title: Detail", we usually want just Title
        # unless it's a specific known safe format. 
        # For security, we might want to be aggressive here.
        clean_message = message.split(":")[0].strip()
        return clean_message
    
    return str(exception)


def _handle_mandatory_error(exception, doc, doctype):
    missing_fields = []
    if doc:
        errors = doc._get_missing_mandatory_fields()
        missing_fields = [er[0] for er in errors]
    
    return build_error_response(
        400,
        _("Required values are missing"),
        "MandatoryError",
        missing_fields
    )

def _handle_link_validation_error(exception, doc, doctype):
    message = sanitize_error_message(exception)
    return build_error_response(400, message, "LinkValidationError")

def _handle_does_not_exist_error(exception, doc, doctype):
    return build_error_response(404, _("Does not exist"), "DoesNotExistError")

def _handle_permission_error(exception, doc, doctype):
    message = frappe.flags.error_message or _("Insufficient permissions")
    return build_error_response(403, message, "PermissionError")

def _handle_overlap_error(exception, doc, doctype):
    message = sanitize_error_message(exception)
    return build_error_response(409, message, "OverlapError")


EXCEPTION_HANDLERS = {
    frappe.MandatoryError: _handle_mandatory_error,
    frappe.LinkValidationError: _handle_link_validation_error,
    frappe.DoesNotExistError: _handle_does_not_exist_error,
    frappe.PermissionError: _handle_permission_error,
    OverlapError: _handle_overlap_error,
}

def handle_exception_response(
    doc, doctype, exception, uploaded_files=[], for_update=False, for_delete=False
):
    """
    Centralized exception handler using registry pattern.
    """
    delete_duplicated_or_after_error(uploaded_files)
    
    http_status_code = getattr(exception, "http_status_code", 500)
    
    # Determine operation title
    if for_delete:
        title = _("failed to update {}").format(_(doctype))
    else:
        title = (
            _("failed to update {}").format(_(doctype))
            if for_update
            else _("failed to create {}").format(_(doctype))
        )

    # Log unexpected errors for debugging (500s)
    if http_status_code == 500:
        frappe.log_error(title=f"API Error: {doctype}", message=frappe.get_traceback())

    # Find specific handler
    handler = EXCEPTION_HANDLERS.get(type(exception))
    if handler:
        return handler(exception, doc, doctype)
    
    # Fallback to general handling
    message = sanitize_error_message(exception)
    return build_error_response(http_status_code, title, message)
