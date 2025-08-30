import frappe
from frappe.utils import cint
from common.api.utils.response import (
    build_response,
    build_error_response,
    build_success_response,
)
from common.api.utils.endpoints import document_list as base_document_list

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
    # "Bonus Request",
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


def document_list(doctype: str, fields: list | str, filters):
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
        # evaluate frappe.get_list
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
        # return build_success_response(200, f"{doctype} fetched", response_data)
    except Exception as exc:
        print(frappe.get_traceback())
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


def employee_requests_list():
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
    order_by=None
    order=None
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
        is_valid, http_status_code, content = document_list(doctype, fields, filters)
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
            response_data.update(content)
            data_list += map(
                lambda x: x.update({"doctype": doctype}),
                content.get("data_list", []),
            )
            totalCount += cint(content.get("totalCount"))
            pageCount += cint(content.get("pageCount"))
    if not has_success:
        return build_error_response(
            status_code=400, message="Failed to Read Employee Requests", error=errors
        )
    if "order_by" in frappe.request.args:
        order_by = frappe.request.args["order_by"]
    if "order" in frappe.request.args:
        order = frappe.request.args["order"]
    reverse=False
    if order and isinstance(order, str) and order.upper() == "DESC":
        reverse=True
    if order_by and isinstance(order_by, str) and order_by.lower() in ["name", "employee", "employee_name", "status", "docstatus", "request_date", "modified", "creation", "doctype"]:
        data_list = sorted(data_list, key=lambda obj: obj[order_by], reverse=reverse)[:limit_page_length]
    else:
        data_list = sorted(data_list, key=lambda obj: obj.modified, reverse=reverse)[:limit_page_length]

    if len(errors) == 0:
        response_data.update(
            {
                "data_list": data_list,
                "perPage": limit_page_length,
                "totalCount": totalCount,
                "pageCount": pageCount,
            }
        )
        return build_success_response(
            status_code=200, message="Employee Requests Fetched", data=response_data
        )
    return build_response(
        status="success",
        status_code=200,
        data=response_data,
        error=errors,
        message="Employee Requests Fetched with Errors",
        missing_data=None,
    )


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
    # Append Date field
    if doctype in ["Loan Application", "Leave Application"]:
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


def employee_requests_state_list():
    doctype = "Workflow State"
    return base_document_list(doctype, ["name", "workflow_state_name", "style"])
