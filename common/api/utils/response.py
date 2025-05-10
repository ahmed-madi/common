
import frappe
from common.api.utils import delete_duplicated_or_after_error

def build_error_response(status_code, message, error, missing_data=None):
    return build_response(status="failed", status_code=status_code, message=message, error=error, missing_data=missing_data)

def build_success_response(status_code, message, data):
    return build_response(status="success", status_code=status_code, message=message, data=data)

def build_response(status=None, status_code=None, data=None, error=None, message=None, missing_data=None):
    frappe.local.response["status"] = status
    frappe.local.response["statusCode"] = status_code
    frappe.local.response["http_status_code"] = status_code
    frappe.local.response["data"] = data
    frappe.local.response["error"] = error
    frappe.local.response["message"] = message
    if missing_data:
        frappe.local.response["missing_data"] = missing_data
    # frappe.local.response["type"] = "json"
    frappe.local.message_log = None
    frappe.local.debug_log = None
    frappe.flags.error_message = None


def handle_exception_response(doc, exception, uploaded_files=[]):
    http_status_code = 500
    message = exception
    delete_duplicated_or_after_error(uploaded_files)

    if hasattr(exception, "http_status_code"):
        http_status_code = exception.http_status_code
    # extract mandatory message
    if isinstance(exception, frappe.MandatoryError):
        errors = doc._get_missing_mandatory_fields()
        missing_fields = [er[0] for er in errors]
        return build_error_response(http_status_code, f"failed to create {doc.doctype}", "Required values are missing", missing_fields)
    elif isinstance(exception, frappe.LinkValidationError):
        if hasattr(exception, "args"):
            args = exception.args
            if len(args) > 0:
                message = args[0]
        return build_error_response(http_status_code, f"failed to create {doc.doctype}", message)
    
    # General exceptions
    if hasattr(exception, "args"):
        args = exception.args
        if len(args) > 0:
            message = args[0].split(":")[0]
            if message == "Cannot link cancelled document":
                message = args[0]
    
    return build_error_response(http_status_code, f"failed to create {doc.doctype}", message)
