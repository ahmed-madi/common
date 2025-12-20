import frappe
from frappe import _, cint
from frappe.utils import getdate, cstr
from werkzeug.routing import Rule
from common.api.utils.resource import BaseResource
from common.api.utils.decorators import safe_api
from common.api.utils.response_data import format_response_data

ACTIVITY_CONFIG = {
    "Company Newsletter": {
        "extra_fields": ["publish_on as date", "subject"],
        "filters": [["published", "=", 1]],
        "date_filter_field": "publish_on",
    },
    "Event": {
        "extra_fields": ["starts_on as date", "subject"],
        "filters": [["published", "=", 1]],
        "date_filter_field": "starts_on",
    },
    "Project": {
        "extra_fields": ["project_name as subject", "expected_start_date as date"],
        "filters": [["expected_start_date", "is", "set"]],
        "date_filter_field": "expected_start_date",
    },
}


def get_activity_config(doctype):
    return ACTIVITY_CONFIG.get(doctype, {})


def get_valid_activity_fields(doctype, from_date=None, to_date=None, date=None):
    config = get_activity_config(doctype)
    base_fields = ["name"]
    base_fields.extend(config.get("extra_fields", []))

    filters = config.get("filters", []).copy()
    date_field = config.get("date_filter_field", "date")

    if from_date or to_date:
        if date_field:
            if from_date and to_date:
                filters.append(
                    [
                        date_field,
                        "between",
                        [f"{from_date} 00:00:00", f"{to_date} 23:59:59"],
                    ]
                )
            elif from_date:
                filters.append([date_field, ">=", f"{from_date} 00:00:00"])
            elif to_date:
                filters.append([date_field, "<=", f"{to_date} 23:59:59"])
    elif date:
        if date_field:
            if len(date) == 10:
                filters.append(
                    [date_field, "between", [f"{date} 00:00:00", f"{date} 23:59:59"]]
                )
            else:
                filters.append([date_field, "=", date])

    return base_fields, filters


def custom_document_list(doctype, fields, filters):
    """
    Fetch documents with pagination independently of arguments
    """
    args = frappe.request.args
    limit_page_length = cint(args.get("limit_page_length", args.get("limit", 20)))
    page = cint(args.get("limit_start", args.get("page", 1)))
    if page < 1:
        page = 1

    limit_start = (page - 1) * limit_page_length

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

        # Count is expensive but kept for compatibility with unified pattern
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


class ActivityResource(BaseResource):
    doctype = "Activity"
    url_prefix = "/company"
    resource_name = "activities"
    add_perms = False
    add_wf = False

    @classmethod
    def list(cls):
        @safe_api
        def _list():
            args = frappe.request.args

            doctypes = (
                [args.get("doctype")]
                if args.get("doctype") in ACTIVITY_CONFIG
                else list(ACTIVITY_CONFIG.keys())
            )

            from_date = args.get("from_date")
            to_date = args.get("to_date")
            date = args.get("date")
            limit = cint(args.get("limit_page_length", args.get("limit", 20)))

            response_data = frappe._dict()
            all_data = []
            errors = []
            total_count = 0
            page_count = 0
            has_success = False

            for doctype in doctypes:
                fields, filters = get_valid_activity_fields(
                    doctype, from_date, to_date, date
                )

                is_valid, code, result = custom_document_list(doctype, fields, filters)

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
                rows = result.get("data_list", [])

                for row in rows:
                    row["doctype"] = doctype
                    if row.get("date"):
                        try:
                            row["date"] = getdate(row["date"])
                        except Exception:
                            pass

                all_data.extend(rows)
                total_count += cint(result.get("totalCount"))
                page_count += cint(result.get("pageCount"))

                response_data.update(result)

            if not has_success and errors:
                frappe.throw(_("Failed to Read Activities: {0}").format(errors))

            order_by = args.get("order_by", "date")
            reverse = args.get("order", "DESC").upper() == "DESC"

            if order_by not in ["name", "subject", "date", "doctype"]:
                order_by = "date"

            try:
                all_data.sort(
                    key=lambda x: cstr(x.get(order_by) or ""), reverse=reverse
                )
            except Exception:
                pass

            final_data = all_data[:limit]

            formatted_data = []
            for row in final_data:
                dt = row.get("doctype")
                formatted_row = format_response_data(
                    dt,
                    [row],
                    add_perms=cls.add_perms,
                    add_wf=cls.add_wf,
                )[0]
                formatted_data.append(formatted_row)

            response_data.update(
                {
                    "data_list": formatted_data,
                    "perPage": limit,
                    "totalCount": total_count,
                    "pageCount": page_count,
                }
            )

            if errors:
                response_data["errors"] = errors
                return response_data, _("Activities fetched with errors")

            return response_data, _("Activities fetched")

        _list.__name__ = "company_activities_list"
        return _list

    @classmethod
    def get_routes(cls):
        name = cls.resource_name
        base_url = f"{cls.url_prefix}/{name}"
        return [Rule(base_url, methods=["GET"], endpoint=cls.list())]
