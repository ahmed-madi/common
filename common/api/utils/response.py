
import frappe
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


