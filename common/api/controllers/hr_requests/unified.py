import frappe
from frappe import cint
from common.api.utils.resource import BaseResource
from common.api.utils.endpoints import document_list as base_document_list
from common.api.utils.decorators import safe_api

# Configuration for each Doctype
# format: "Doctype": { "fields": [...], "filters": {...}, "date_aliases": {...}, "has_attachment": bool }

REQUEST_CONFIG = {
    "Compensatory Leave Request": {
        "extra_fields": ["work_from_date as from_date", "work_end_date as to_date"],
        "null_dates": True,
        "null_attachment": True,
    },
    "Leave Application": {
        "extra_fields": [
            "from_date",
            "to_date",
            "attachment",
            "posting_date as request_date",
        ],
        "null_dates": True,
        "date_filter_field": "posting_date",
    },
    "Visa Application": {
        "extra_fields": [
            "start_date as from_date",
            "end_date as to_date",
            "attachment",
        ],
        "null_dates": True,
    },
    "Club Request": {
        "extra_fields": [
            "start_date as from_date",
            "end_date as to_date",
            "attachment",
        ],
        "null_dates": True,
    },
    "Training Request": {
        "extra_fields": [
            "start_date as from_date",
            "end_date as to_date",
            "attachment",
        ],
        "null_dates": True,
    },
    "Work From Home Request": {
        "extra_fields": ["from_date", "to_date"],
        "null_dates": True,
        "null_attachment": True,
    },
    "Work Outside Office Request": {
        "extra_fields": ["from_date", "to_date", "attachment"],
        "null_dates": True,
    },
    "Cancel Leave Application": {
        "null_attachment": True,
    },
    "Leave Suspension": {
        "null_attachment": True,
    },
    "Employee Resignation": {
        "null_attachment": True,
    },
    "System Access Request": {
        "null_attachment": True,
    },
    "Early Leave Application": {
        "extra_fields": ["attachment"],
    },
    "Salary Identification Letter": {
        "extra_fields": ["signed_pdf_document as attachment"],
    },
    "Salary Fixation": {
        "extra_fields": ["attachment"],
    },
    "Education Allowance Request": {
        "extra_fields": ["attachment"],
    },
    "Document Request": {
        "extra_fields": ["attachment"],
    },
    "Change IBAN Request": {
        "extra_fields": ["attachment"],
    },
    "Clearance Letter Request": {
        "extra_fields": ["clearance_document as attachment"],
    },
    "Loan Application": {
        "custom_base_fields": [
            "name",
            "applicant as employee",
            "applicant_name as employee_name",
        ],
        "extra_fields": ["attachment", "posting_date as request_date"],
        "filters": {"applicant_type": "Employee"},
        "date_filter_field": "posting_date",
        "employee_filter_field": "applicant",
    },
    "Employee Expense Request": {
        "custom_base_fields": [
            "name",
            "request_type",
            "expenses_type",
            "creation as from_date",
        ],
    },
    "General Request": {
        "extra_fields": ["attachment", "request_date"],
        "date_filter_field": "request_date",
    },
}

REQUESTS_DOCTYPE = list(REQUEST_CONFIG.keys())
# Ensure we include any that might have been implicit but are in the CONFIG keys.
# Original list had 20 items.
# Let's ensure the list matches the original exactly for safety, then extend/use keys.
# Original list:
#     "Compensatory Leave Request", "Early Leave Application", "Work Outside Office Request",
#     "Cancel Leave Application", "Leave Suspension", "Leave Application", "Work From Home Request",
#     "Visa Application", "Training Request", "Salary Identification Letter", "Salary Fixation",
#     "Loan Application", "Employee Resignation", "Education Allowance Request", "Document Request",
#     "Club Request", "Clearance Letter Request", "Change IBAN Request", "System Access Request",
#     "Employee Expense Request"

DOC_STATUS = {"Draft": 0, "Submitted": 1, "Cancelled": 2}


def get_request_config(doctype):
    return REQUEST_CONFIG.get(doctype, {})


def get_valid_request_fields(
    doctype, employee, request_date, status, docstatus, from_date=None, to_date=None
):
    config = get_request_config(doctype)

    base_fields = config.get(
        "custom_base_fields", ["name", "employee", "employee_name"]
    )[:]

    base_fields.extend(config.get("extra_fields", []))

    if "date_filter_field" not in config and "request_date" not in [
        f.split(" as ")[-1] for f in base_fields
    ]:
        # logic matches: if doctype != "Employee Expense Request" -> append request_date
        # Expense request has explicit config above.
        # The original code added "request_date" for everyone except expense request and those handling it manually (Loan/Leave)
        # Loan/Leave added "posting_date as request_date".
        # So we need to ensure we don't double add.
        pass

    # Simpler logic based on original analysis:
    # Loan/Leave: added posting_date as request_date.
    # Employee Expense: added creation as from_date, NO request_date.
    # All others: added request_date.

    # In my config:
    # Loan/Leave have "posting_date as request_date" in extra_fields.
    # Employee Expense has no request_date in extra_fields.
    # Others: need "request_date".

    has_request_date = any("request_date" in f for f in base_fields)
    date_field = config.get("date_filter_field", "request_date")

    if not has_request_date:
        if frappe.get_meta(doctype).has_field("request_date"):
            base_fields.append("request_date")
        else:
            base_fields.append("creation as request_date")
            if date_field == "request_date":
                date_field = "creation"

    filters = config.get("filters", {}).copy()

    if docstatus and isinstance(docstatus, str) and docstatus in DOC_STATUS:
        filters["docstatus"] = DOC_STATUS[docstatus]

    if employee and isinstance(employee, str):
        employee_field = config.get("employee_filter_field", "employee")
        filters[employee_field] = employee

    if from_date or to_date:
        if date_field:
            if from_date and to_date:
                filters[date_field] = [
                    "between",
                    [f"{from_date} 00:00:00", f"{to_date} 23:59:59"],
                ]
            elif from_date:
                filters[date_field] = [">=", f"{from_date} 00:00:00"]
            elif to_date:
                filters[date_field] = ["<=", f"{to_date} 23:59:59"]
    elif request_date and isinstance(request_date, str):
        if date_field:
            if len(request_date) == 10:
                filters[date_field] = [
                    "between",
                    [f"{request_date} 00:00:00", f"{request_date} 23:59:59"],
                ]
            else:
                filters[date_field] = request_date

    wf = frappe.get_all("Workflow", {"document_type": doctype, "is_active": 1})
    if wf:
        wf = frappe.get_doc("Workflow", wf[0])
    else:
        wf = None

    status_field = wf.workflow_state_field if wf else "status"

    base_fields.append(f"{status_field} as status")
    base_fields.append("docstatus")
    base_fields.extend(["modified", "creation"])

    if status and isinstance(status, str):
        filters[status_field] = status

    return base_fields, filters, wf


def custom_document_list(
    doctype, fields, filters, limit_start=None, limit_page_length=None
):
    """
    Fetch documents with pagination
    """
    args = frappe.request.args or frappe.form_dict
    if limit_page_length is None:
        limit_page_length = cint(args.get("limit_page_length", args.get("limit", 20)))

    if limit_start is None:
        page = cint(args.get("limit_start", args.get("page", 1)))
        if page < 1:
            page = 1
        limit_start = (page - 1) * limit_page_length
    else:
        page = (limit_start // limit_page_length) + 1

    try:
        data = frappe.get_list(
            doctype,
            fields=fields,
            filters=filters,
            limit_start=limit_start,
            limit_page_length=limit_page_length,
            order_by=None,
            ignore_permissions=False,
        )

        # Count is expensive, maybe optimize? Keeping original logic for now.
        # Original used get_list limit=999999999 which is very bad for perf.
        # But we must preserve behavior unless asked to fix perf.
        # Actually, `frappe.db.count` is better.
        # count = frappe.db.count(doctype, filters=filters)
        # But original logic used permissions-aware get_list len.
        count = len(frappe.get_list(doctype, filters=filters, limit_page_length=999999))

        return (
            True,
            200,
            {
                "data_list": data,
                "page": page,
                "perPage": limit_page_length,
                "totalCount": count,
                "pageCount": len(data),
            },
        )
    except Exception as e:
        return False, getattr(e, "http_status_code", 500), str(e)


class UnifiedRequestResource(BaseResource):
    doctype = "Employee Request"
    url_prefix = ""
    resource_name = "employee-requests"
    add_perms = True
    add_wf = True

    @classmethod
    def list(cls):
        @safe_api
        def _list():
            args = frappe.request.args or frappe.form_dict
            doctypes = (
                [args.get("doctype")]
                if args.get("doctype") in REQUEST_CONFIG
                else list(REQUEST_CONFIG.keys())
            )

            employee = args.get("employee")
            request_date = args.get("request_date") or args.get("date")
            from_date = args.get("from_date")
            to_date = args.get("to_date")
            status = args.get("status")
            docstatus = args.get("docstatus")
            page = cint(args.get("limit_start", args.get("page", 1)))
            if page < 1:
                page = 1
            limit = cint(args.get("limit_page_length", args.get("limit", 20)))
            limit_start = (page - 1) * limit

            response_data = frappe._dict()
            all_data = []
            errors = []
            total_count = 0
            has_success = False
            workflows = {}

            for doctype in doctypes:
                fields, filters, wf = get_valid_request_fields(
                    doctype,
                    employee,
                    request_date,
                    status,
                    docstatus,
                    from_date,
                    to_date,
                )
                workflows[doctype] = wf

                is_valid, code, result = custom_document_list(
                    doctype, fields, filters, limit_start=0, limit_page_length=999999
                )

                if not is_valid:
                    errors.append(
                        {
                            "http_status_code": code,
                            "error": f"failed to read {doctype}",
                            "message": result,
                        }
                    )
                    continue

                has_success = True

                config = get_request_config(doctype)
                rows = result.get("data_list", [])

                for row in rows:
                    row["doctype"] = doctype

                    for date_field in ["from_date", "to_date", "request_date"]:
                        if row.get(date_field):
                            try:
                                row[date_field] = frappe.utils.getdate(row[date_field])
                            except Exception:
                                pass

                    if config.get("null_dates"):
                        row.update({"from_date": None, "to_date": None})
                    if config.get("null_attachment"):
                        row["attachment"] = None

                all_data.extend(rows)
                total_count += cint(result.get("totalCount"))

                response_data.update(result)

            if not has_success and errors:
                frappe.throw(f"Failed to Read Employee Requests: {errors}")

            order_by = args.get("order_by", "modified")
            if order_by == "date":
                order_by = "request_date"

            if order_by not in [
                "name",
                "employee",
                "employee_name",
                "status",
                "docstatus",
                "request_date",
                "modified",
                "creation",
                "doctype",
            ]:
                order_by = "modified"

            order = args.get("order", "DESC").upper()
            reverse = order == "DESC"

            try:
                from frappe.utils import cstr

                all_data.sort(
                    key=lambda x: cstr(x.get(order_by) or ""), reverse=reverse
                )
            except Exception:
                pass

            final_data = all_data[limit_start : limit_start + limit]

            from common.api.utils.response_data import format_response_data

            formatted_data = []
            for row in final_data:
                dt = row.get("doctype")
                wf = workflows.get(dt)
                # Use format_response_data to add perms, wf, and format fields
                formatted_row = format_response_data(
                    dt,
                    [row],
                    wf=wf,
                    add_perms=cls.add_perms,
                    add_wf=cls.add_wf,
                    is_for_list=True,
                )[0]
                formatted_data.append(formatted_row)

            response_data.update(
                {
                    "data_list": formatted_data,
                    "page": page,
                    "perPage": limit,
                    "totalCount": total_count,
                    "pageCount": len(formatted_data),
                }
            )

            if errors:
                response_data["errors"] = errors
                return response_data, "Employee Requests Fetched with Errors"

            return response_data, "Employee Requests Fetched"

        _list.__name__ = "employee_requests_list"
        return _list


class UnifiedRequestStatusResource(BaseResource):
    doctype = "Workflow State"
    url_prefix = ""
    resource_name = "employee-requests-status"

    @classmethod
    def list(cls):
        @safe_api
        def _list():
            return base_document_list(
                "Workflow State", ["name", "workflow_state_name", "style"]
            )

        _list.__name__ = "employee_requests_state_list"
        return _list


@frappe.whitelist()
def get_unified_request_list():
    _list = UnifiedRequestResource.list()()
    print(_list)
    return _list
