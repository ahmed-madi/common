import frappe
from frappe import cint
from common.api.utils.resource import BaseResource
from common.api.utils.endpoints import document_list as base_document_list
from common.api.utils.decorators import safe_api

NULL_FROM_TO_DATES = [
    "Compensatory Leave Request",
    "Leave Application",
    "Visa Application",
    "Club Request",
    "Training Request",
    "Work From Home Request",
    "Work Outside Office Request",
]
NULL_ATTACHMENT = [
    "Compensatory Leave Request",
    "Cancel Leave Application",
    "Leave Suspension",
    "Work From Home Request",
    "Employee Resignation",
    "System Access Request",
]
REQUESTS_DOCTYPE = [
    "Compensatory Leave Request",
    "Early Leave Application",
    "Work Outside Office Request",
    "Cancel Leave Application",
    "Leave Suspension",
    "Leave Application",
    "Work From Home Request",
    "Visa Application",
    "Training Request",
    "Salary Identification Letter",
    "Salary Fixation",
    "Loan Application",
    "Employee Resignation",
    "Education Allowance Request",
    "Document Request",
    "Club Request",
    "Clearance Letter Request",
    "Change IBAN Request",
    "System Access Request",
]

REQUESTS_DOCTYPE_FIELDS = {
    "Loan Application": [
        "name",
        "applicant as employee",
        "applicant_name as employee_name",
    ]
}
DOC_STATUS = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

def get_valid_request_fields(doctype, employee, request_date, status, docstatus):
    BASE_FIELDS = REQUESTS_DOCTYPE_FIELDS.get(
        doctype, ["name", "employee", "employee_name"]
    )
    FILTERS = {}
    if docstatus and isinstance(docstatus, str):
        if docstatus in DOC_STATUS:
            FILTERS.update({"docstatus": DOC_STATUS.get(docstatus)})
    if doctype == "Loan Application":
        FILTERS.update({"applicant_type": "Employee"})
    # Update Filters
    if employee and isinstance(employee, str):
        if doctype == "Loan Application":
            FILTERS.update(
                {
                    "applicant": employee,
                }
            )
        else:
            FILTERS.update(
                {
                    "employee": employee,
                }
            )
    # Append from/to Dates and attachment field field
    if doctype == "Compensatory Leave Request":
        BASE_FIELDS.append("work_from_date as from_date")
        BASE_FIELDS.append("work_end_date as to_date")
    elif doctype == "Leave Application":
        BASE_FIELDS.append("from_date")
        BASE_FIELDS.append("to_date")
    elif doctype == "Visa Application":
        BASE_FIELDS.append("start_date as from_date")
        BASE_FIELDS.append("end_date as to_date")
        BASE_FIELDS.append("attachment")
    elif doctype == "Club Request":
        BASE_FIELDS.append("start_date as from_date")
        BASE_FIELDS.append("end_date as to_date")
        BASE_FIELDS.append("attachment")
    elif doctype == "Training Request":
        BASE_FIELDS.append("start_date as from_date")
        BASE_FIELDS.append("end_date as to_date")
        BASE_FIELDS.append("attachment")
    elif doctype == "Work From Home Request":
        BASE_FIELDS.append("from_date")
        BASE_FIELDS.append("to_date")
    elif doctype == "Work Outside Office Request":
        BASE_FIELDS.append("from_date")
        BASE_FIELDS.append("to_date")
        BASE_FIELDS.append("attachment")
    elif doctype == "Early Leave Application":
        BASE_FIELDS.append("attachment")
    elif doctype == "Salary Identification Letter":
        BASE_FIELDS.append("signed_pdf_document as attachment")
    elif doctype == "Salary Fixation":
        BASE_FIELDS.append("attachment")
    elif doctype == "Education Allowance Request":
        BASE_FIELDS.append("attachment")
    elif doctype == "Document Request":
        BASE_FIELDS.append("attachment")
    elif doctype == "Change IBAN Request":
        BASE_FIELDS.append("attachment")
    elif doctype == "Clearance Letter Request":
        BASE_FIELDS.append("clearance_document as attachment")
    

    if doctype in ["Loan Application", "Leave Application"]:
        BASE_FIELDS.append("attachment")
        BASE_FIELDS.append("posting_date as request_date")
        if request_date and isinstance(request_date, str):
            FILTERS.update(
                {
                    "posting_date": request_date,
                }
            )
    else:
        BASE_FIELDS.append("request_date")
        if request_date and isinstance(request_date, str):
            FILTERS.update(
                {
                    "request_date": request_date,
                }
            )

    # Append Status Fields
    status_field = (
        frappe.db.get_value(
            "Workflow",
            {"is_active": 1, "document_type": doctype},
            "workflow_state_field",
        )
        or "status"
    )
    BASE_FIELDS.append(f"{status_field} as status")
    BASE_FIELDS.append("docstatus")
    BASE_FIELDS += ["modified", "creation"]
    # Update Filters
    if status and isinstance(status, str):
        FILTERS.update(
            {
                f"{status_field}": status,
            }
        )
    return BASE_FIELDS, FILTERS

def custom_document_list(doctype, fields, filters): # Local rewrite of document_list logic from init
    or_filters = None
    group_by = None
    order_by = None
    limit_start = 0
    limit_page_length = 20
    parent = None

    if "limit_page_length" in frappe.request.args:
        limit_page_length = cint(frappe.request.args["limit_page_length"])
    if "limit" in frappe.request.args:
        limit_page_length = cint(frappe.request.args["limit"])
    if "limit_start" in frappe.request.args:
        limit_start = cint(frappe.request.args["limit_start"]) - 1
        if limit_start < 0:
            limit_start = 1
    if "page" in frappe.request.args:
        limit_start = cint(frappe.request.args["page"]) - 1
        if limit_start < 0:
            limit_start = 1
    limit_start = limit_start * limit_page_length

    try:
        args = frappe._dict(
            parent_doctype=parent,
            fields=fields,
            filters=filters,
            or_filters=or_filters,
            group_by=group_by,
            order_by=order_by,
            limit_start=limit_start,
            limit_page_length=limit_page_length,
            as_list=False,
        )
        count = len(frappe.get_list(doctype, limit_page_length=999999999))
        data = frappe.call(frappe.client.get_list, doctype, **args)
        response_data = frappe._dict()
        response_data.update(
            {
                "data_list": data,
                "page": limit_start + 1,
                "perPage": limit_page_length,
                "totalCount": count,
                "pageCount": len(data),
            }
        )
        return True, 200, response_data
    except Exception as exc:
        # print(frappe.get_traceback())
        http_status_code = 500
        message = exc
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 1 and isinstance(args[0], int):
                message = args[1]
            elif len(args) > 0:
                message = args[0].split(":")[0]
        return False, http_status_code, message


class UnifiedRequestResource(BaseResource):
    doctype = "Employee Request"  # Virtual aggregate doctype
    url_prefix = "/"
    resource_name = "employee-requests"
    
    @classmethod
    def list(cls):
        @safe_api
        def _list():
            data_list = []
            errors = []
            totalCount = 0
            pageCount = 0
            has_success = False
            limit_page_length = 20
            doctype = None
            employee = None
            request_date = None
            status = None
            docstatus = None
            order_by = None
            order = None
            response_data = frappe._dict()

            if "limit_page_length" in frappe.request.args:
                limit_page_length = cint(frappe.request.args["limit_page_length"])
            if "limit" in frappe.request.args:
                limit_page_length = cint(frappe.request.args["limit"])
            
            REQUESTS_DOCTYPE_TO_SELECT = REQUESTS_DOCTYPE
            if "doctype" in frappe.request.args:
                doctype = frappe.request.args["doctype"]
                if doctype in REQUESTS_DOCTYPE:
                    REQUESTS_DOCTYPE_TO_SELECT = [doctype]
            if "employee" in frappe.request.args:
                employee = frappe.request.args["employee"]
            if "request_date" in frappe.request.args:
                request_date = frappe.request.args["request_date"]
            if "status" in frappe.request.args:
                status = frappe.request.args["status"]
            if "docstatus" in frappe.request.args:
                docstatus = frappe.request.args["docstatus"]

            for doctype in REQUESTS_DOCTYPE_TO_SELECT:
                fields, filters = get_valid_request_fields(
                    doctype, employee, request_date, status, docstatus
                )
                
                # Call local custom list since generic one doesn't match return format of this Aggregator
                is_valid, http_status_code, content = custom_document_list(doctype, fields, filters)
                
                if not is_valid:
                    errors.append(
                        {
                            "http_status_code": http_status_code,
                            "error": f"failed to read {doctype}",
                            "message": content,
                        }
                    )
                else:
                    has_success = True
                    # content is dict with data_list
                    response_data.update(content) # This overwrites response_data page metadata? NO, logic was merging?
                    # Original logic updated response_data with content (so last one wins metadata)
                    # And aggregated data_list.
                    
                    dl = content.get("data_list", [])
                    for x in dl:
                        if doctype not in NULL_FROM_TO_DATES:
                            x.update({"doctype": doctype})
                        else:
                            x.update(
                                {"doctype": doctype, "from_date": None, "to_date": None}
                            )
                        if doctype in NULL_ATTACHMENT:
                            x.update({
                                "attachment": None,
                            })
                    data_list += dl

                    totalCount += cint(content.get("totalCount"))
                    pageCount += cint(content.get("pageCount"))
            
            if not has_success:
                 # safe_api will wrap exceptions, but here we return error response dict?
                 # original returned build_error_response.
                 # safe_api returns json directly?
                 # I'll return dict for safe_api to wrap?
                 # No, safe_api expects success tuple (data, msg) OR raises error.
                 # I should raise exception if failure.
                 frappe.throw("Failed to Read Employee Requests: " + str(errors))
            
            if "order_by" in frappe.request.args:
                order_by = frappe.request.args["order_by"]
            if "order" in frappe.request.args:
                order = frappe.request.args["order"]
            reverse = False
            if order and isinstance(order, str) and order.upper() == "DESC":
                reverse = True
                
            # Sort logic...
            key_sort = "modified"
            if (order_by and isinstance(order_by, str) and order_by.lower() in [
                "name", "employee", "employee_name", "status", "docstatus", 
                "request_date", "modified", "creation", "doctype"]):
                    key_sort = order_by
            
            # Using safe try-catch for sort key might be needed if key missing
            try:
                data_list = sorted(data_list, key=lambda obj: obj.get(key_sort, ""), reverse=reverse)
            except:  # noqa: E722
                pass # fallback
            
            data_list = data_list[:limit_page_length]

            if len(errors) == 0:
                response_data.update(
                    {
                        "data_list": data_list,
                        "perPage": limit_page_length,
                        "totalCount": totalCount,
                        "pageCount": pageCount,
                    }
                )
                return response_data, "Employee Requests Fetched"
            else:
                 # "Employee Requests Fetched with Errors"
                 # return data with error metadata
                 response_data.update({"errors": errors})
                 return response_data, "Employee Requests Fetched with Errors"

        _list.__name__ = "employee_requests_list"
        return _list

class UnifiedRequestStatusResource(BaseResource):
    doctype = "Workflow State"  # Uses Workflow State doctype
    url_prefix = "/"
    resource_name = "employee-requests-status"
    
    @classmethod
    def list(cls):
        @safe_api
        def _list():
            doctype = "Workflow State"
            # base_document_list returns response object?
            # base_document_list logic in endpoints.py returns build_success_response usually.
            # I should use document_list helper or re-implement.
            # Original: return base_document_list(doctype, ["name", "workflow_state_name", "style"])
            return base_document_list(doctype, ["name", "workflow_state_name", "style"])
        _list.__name__ = "employee_requests_state_list"
        return _list
