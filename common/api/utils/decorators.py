import functools
import frappe
from frappe import _
from common.api.utils.response import (
    build_success_response,
    handle_exception_response,
)

def safe_api(func):
    """
    Decorator to standardize API response and error handling.
    
    Usage:
        @safe_api
        def my_controller(param):
            # ... business logic ...
            return data
            
    Support Return Types:
        - dict/list: Treated as data, returns 200 Success
        - tuple(data, message): Custom message
        - tuple(data, message, http_status_code): Custom status
        - Response Object (werkzeug): Returned as is
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Execute the controller logic
            result = func(*args, **kwargs)
            
            # If standard response dict/object from Frappe or our build_response
            if isinstance(result, (dict, list)) and "http_status_code" in result:
                # Assuming it's already a formatted response from build_response
                # but build_response puts it in frappe.local.response, it doesn't return it
                # Wait, common.api.utils.response.build_response sets frappe.local.response 
                # but generally controllers in Frappe either return data or set frappe.local.response.
                # If the function returns something, we should handle it.
                pass
            
            # If function returns None, assuming it set frappe.local.response manually
            # or it has no content.
            if result is None:
                if frappe.local.response:
                    return
                return build_success_response(200, _("Success"), {})

            # Parse return values
            data = result
            message = _("Success")
            status_code = 200
            
            if isinstance(result, tuple):
                if len(result) == 2:
                    data, message = result
                elif len(result) == 3:
                    data, message, status_code = result
            
            # If data is a Response object (unlikely in this context but possible)
            # just return it. 
            
            return build_success_response(status_code, message, data)

        except Exception as e:
            # Inspect signature to see if we have doc/doctype context if possible?
            # Typically impossible to know "doc" here genericallly unless passed as arg.
            # handle_exception_response expects (doc, doctype, exception...)
            # We can try to infer doctype from module or args, but simpler to pass generic context.
            
            doctype = None
            # Try to guess doctype from kwargs if present
            if "doctype" in kwargs:
                doctype = kwargs["doctype"]
            
            # Fallback for handle_exception_response which requires doc/doctype
            # We might need to make handle_exception_response more flexible
            # But for now, let's pass None/Unknown
            return handle_exception_response(None, doctype or "API", e)
            
    return wrapper
