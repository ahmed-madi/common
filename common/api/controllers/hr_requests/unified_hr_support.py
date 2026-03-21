import frappe
from frappe import cint
from common.api.utils.resource import BaseResource
from common.api.utils.endpoints import document_list as base_document_list
from common.api.utils.decorators import safe_api

# Configuration for HR Support Doctypes
HR_SUPPORT_CONFIG = {
    "General Request": {
        "extra_fields": ["title", "message", "attachment", "request_type"],
        "date_filter_field": "request_date",
    },
    "Department Contact": {
        "custom_base_fields": [
            "name",
            "from_employee as employee",
            "employee_name",
        ],
        "extra_fields": ["subject", "message", "department", "request_date"],
        "employee_filter_field": "from_employee",
        "date_filter_field": "request_date",
    },
    "Employee Inquiry": {
        "extra_fields": [
            "subject",
            "message",
            "attachment",
            "management_area",
            "request_date",
        ],
        "date_filter_field": "request_date",
    },
    "HR Ticket": {
        "extra_fields": [
            "subject",
            "description",
            "status as ticket_status",
            "priority",
            "issue_type",
            "attachment",
            "opening_date as request_date",
        ],
        "date_filter_field": "opening_date",
    },
}

DOC_STATUS = {"Draft": 0, "Submitted": 1, "Cancelled": 2}


def get_request_config(doctype):
    return HR_SUPPORT_CONFIG.get(doctype, {})


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
        pass

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


class HRSupportResource(BaseResource):
    doctype = "HR Support Request"
    url_prefix = ""
    resource_name = "employee-support-requests"
    add_perms = True
    add_wf = True

    @classmethod
    def list(cls):
        @safe_api
        def _list():
            args = frappe.request.args or frappe.form_dict
            doctypes = (
                [args.get("doctype")]
                if args.get("doctype") in HR_SUPPORT_CONFIG
                else list(HR_SUPPORT_CONFIG.keys())
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
                frappe.throw(f"Failed to Read HR Support Requests: {errors}")

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
                return response_data, "HR Support Requests Fetched with Errors"

            return response_data, "HR Support Requests Fetched"

        _list.__name__ = "hr_support_requests_list"
        return _list


class HRSupportStatusResource(BaseResource):
    doctype = "Workflow State"
    url_prefix = ""
    resource_name = "hr-support-requests-status"

    @classmethod
    def list(cls):
        @safe_api
        def _list():
            return base_document_list(
                "Workflow State", ["name", "workflow_state_name", "style"]
            )

        _list.__name__ = "hr_support_requests_state_list"
        return _list


@frappe.whitelist()
def get_hr_support_list():
    return HRSupportResource.list()()
