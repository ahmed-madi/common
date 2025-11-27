from dateutil.parser import ParserError

import frappe
from frappe.utils import cstr, cint, flt, getdate, get_datetime, get_time


DOCTYPE_ALLOWED_FILTERS = {
    "Clearance Letter Purpose": ["name", "purpose"],
    "Club": ["name", "club_name"],
    "Department": ["name", "department_name", "is_group"],
    "Employee": [
        "name",
        "employee_name",
        "department",
        "designation",
        "date_of_joining",
    ],
    "Task": [
        "name",
        "priority",
        "status",
        "project",
        "exp_start_date",
        "exp_end_date",
    ],
    "Fiscal Year": ["name", "year_start_date", "year_end_date"],
    "Fixation Reason": ["name", "fixation_reason"],
    "Project": ["name", "project_name", "priority", "status", "is_active"],
    "Holiday List": [
        "name",
        "holiday_list_name",
        "from_date",
        "to_date",
        "total_holidays",
        "color",
    ],
    "Language": ["name", "language_name"],
    "Leave Type": [
        "name",
        "leave_type_name",
        "max_leaves_allowed",
    ],
    "Loan Product": ["name", "product_name", "is_term_loan"],
    "Salary Component": [
        "name",
        "salary_component",
        "salary_component_abbr",
        "type",
    ],
    "System Access Level": ["name", "access_level"],
    "Work Type": ["name", "type"],
}
DOCTYPE_ALLOWED_CUSTOM_FILTERS = {}
DATA_FIELDS = [
    "Autocomplete",
    "Data",
    "Color",
    "Text",
    "Small Text",
    "Text Editor",
    "HTML Editor",
    "Long Text",
    "JSON",
    "Code",
    "Phone",
    "Link",
    "Dynamic Link",
    "Select",
    "Email",
    "URL",
    "Read Only",
    "Markdown Editor",
]
FLOAT_NUMBER_FIELDS = ["Currency", "Float", "Percent", "Rating"]
DEFAULT_COLUMNS = [
    "name",
    "creation",
    "modified",
    "modified_by",
    "owner",
    "docstatus",
    "idx",
]


def _get_valid_fields(doctype, meta):
    return [f.fieldname for f in meta.fields] + DEFAULT_COLUMNS


# For listview get request only
def setup_request_data(
    doctype,
    user_filters=[],
    force_user_filters=False,
):
    page = 0
    page_length = 20
    order_by = "modified desc"
    filters = []

    allowed_filters = DOCTYPE_ALLOWED_FILTERS.get(doctype, ["name"])
    if "page" in frappe.request.args:
        page = cint(frappe.request.args["page"]) - 1
        if page < 0:
            page = 0
    if "limit" in frappe.request.args:
        page_length = cint(frappe.request.args["limit"])
        if page_length <= 0:
            page_length = 20
    if "order_by" in frappe.request.args:
        order_by = cstr(frappe.request.args["order_by"]).split(" ")
        if len(order_by) != 2:
            order_by = "modified desc"
        else:
            field_name = order_by[0]
            order_type = order_by[1]
            if order_type.lower() not in ["desc", "asc"]:
                order_by = "modified desc"
            elif field_name not in allowed_filters:
                order_by = "modified desc"
            else:
                order_by = f"{field_name} {order_type}"

    meta = frappe.get_meta(doctype)
    filters += get_valid_filters(
        doctype, meta, user_filters=user_filters, force_user_filters=force_user_filters
    )
    filters += add_custom_filters(doctype)
    or_filters = add_search_params(doctype, meta)

    return page, page_length, order_by, filters, or_filters


def get_valid_filters(
    doctype,
    meta,
    user_filters=[],
    force_user_filters=False,
):
    user_filters_keys = [f[0] for f in user_filters]
    allowed_filters = DOCTYPE_ALLOWED_FILTERS.get(doctype, ["name"])
    filters = []
    for filter_key in allowed_filters:
        value = None
        if filter_key in user_filters_keys and force_user_filters:
            continue
        if filter_key in frappe.request.args:
            value = cstr(frappe.request.args[filter_key])
        if value is None or not value:
            continue

        if filter_key not in DEFAULT_COLUMNS:
            field_type = meta.get_field(filter_key).fieldtype
            if field_type in DATA_FIELDS:
                if len(value) > 0:
                    filters.append([filter_key, "=", value])
            elif field_type == "Date":
                try:
                    value = getdate(value)
                    filters.append([filter_key, "=", value])
                except ParserError:
                    pass
            elif field_type == "Datetime":
                try:
                    value = get_datetime(value)
                    filters.append([filter_key, "like", f"%{value}%"])
                except ParserError:
                    pass
            elif field_type == "Time":
                try:
                    value = get_time(value)
                    filters.append([filter_key, "=", value])
                except ParserError:
                    pass
            elif field_type == "Int":
                value = cint(value)
                filters.append([filter_key, "=", value])
            elif field_type in FLOAT_NUMBER_FIELDS:
                value = flt(value)
                filters.append([filter_key, "=", value])
            elif field_type == "Check":
                if value.lower() == "yes":
                    filters.append([filter_key, "=", 1])
                elif value.lower() == "no":
                    filters.append([filter_key, "=", 0])
        else:
            if filter_key in ["name", "modified_by", "owner"]:
                if len(value) > 0:
                    filters.append([filter_key, "=", value])
            elif filter_key in ["creation", "modified"]:
                try:
                    value = get_datetime(value)
                    filters.append([filter_key, "=", value])
                except ParserError:
                    pass
            elif filter_key == "docstatus":
                value = cint(value)
                if value in [0, 1, 2]:
                    filters.append([filter_key, "=", value])
    filters += user_filters
    return filters


def add_custom_filters(doctype):
    filters = []
    allowed_filters = DOCTYPE_ALLOWED_CUSTOM_FILTERS.get(doctype)

    return filters


def add_search_params(doctype, meta):
    filters = []
    search_fields = ["name"]
    search_fields += list(
        map(lambda x: x.strip(), (meta.search_fields or "").split(","))
    )
    search_fields = set(search_fields)

    if "q" in frappe.request.args:
        value = cstr(frappe.request.args["q"]).strip()
        if len(value) > 0:
            for field in search_fields:
                filters.append([field, "like", f"%{value}%"])
    return filters
