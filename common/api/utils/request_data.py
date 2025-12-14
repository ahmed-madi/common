from dateutil.parser import ParserError

import frappe
from frappe import _
from frappe.utils import cstr, cint, flt, getdate, get_datetime, get_time

# Validation constants to prevent abuse
MAX_PAGE_LENGTH = 1000  # Maximum records per page
MAX_PAGE_NUMBER = 10000  # Maximum page number
DEFAULT_PAGE_LENGTH = 20  # Default records per page

# Filter operators for advanced filtering
# Usage: ?field_name_gte=value (greater than or equal)
FILTER_OPERATORS = {
    "eq": "=",      # Equal (default)
    "ne": "!=",     # Not equal
    "gt": ">",      # Greater than
    "gte": ">=",    # Greater than or equal
    "lt": "<",      # Less than
    "lte": "<=",    # Less than or equal
    "like": "like", # Like pattern
    "in": "in",     # In list
}


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


def parse_filter_with_operator(filter_key):
    """
    Parse filter key to extract field name and operator
    
    Args:
        filter_key: Filter key from request (e.g., "from_date_gte")
    
    Returns:
        tuple: (field_name, operator) e.g., ("from_date", ">=")
        
    Examples:
        >>> parse_filter_with_operator("from_date_gte")
        ("from_date", ">=")
        >>> parse_filter_with_operator("status_ne")
        ("status", "!=")
        >>> parse_filter_with_operator("name")
        ("name", "=")
    """
    # Check for operator suffix
    for op_suffix, op_symbol in FILTER_OPERATORS.items():
        if filter_key.endswith(f"_{op_suffix}"):
            actual_field = filter_key[:-len(f"_{op_suffix}")]
            return actual_field, op_symbol
    
    # Default to equality
    return filter_key, "="


def parse_order_by(order_by_str, allowed_filters):
    """
    Parse order_by string supporting multiple fields
    
    Args:
        order_by_str: Order by string from request (e.g., "department asc, name desc")
        allowed_filters: List of allowed filter fields
    
    Returns:
        str: Validated SQL ORDER BY clause
        
    Examples:
        >>> parse_order_by("name asc", ["name", "status"])
        "name asc"
        >>> parse_order_by("department asc, name desc", ["department", "name"])
        "department asc, name desc"
        >>> parse_order_by("invalid_field asc", ["name"])
        "modified desc"
    """
    if not order_by_str:
        return "modified desc"
    
    order_parts = []
    for part in order_by_str.split(","):
        part = part.strip().split()
        if len(part) != 2:
            continue
        
        field_name, order_type = part
        
        # Validate order type
        if order_type.lower() not in ["desc", "asc"]:
            continue
        
        # Validate field name is in allowed filters or DEFAULT_COLUMNS
        if field_name not in allowed_filters and field_name not in DEFAULT_COLUMNS:
            continue
        
        order_parts.append(f"{field_name} {order_type}")
    
    return ", ".join(order_parts) if order_parts else "modified desc"


def get_allowed_filters(doctype):
    """
    Get allowed filters for a doctype
    Priority:
    1. Custom field on DocType (api_allowed_filters)
    2. Hardcoded DOCTYPE_ALLOWED_FILTERS
    3. Default ["name"]
    """
    # Check if doctype has custom allowed filters configured
    # This allows adding filters without changing code
    try:
        custom_config = frappe.db.get_value("DocType", doctype, "api_allowed_filters")
        if custom_config:
            return frappe.parse_json(custom_config)
    except Exception:
        # Fail silently and fall back to hardcoded defaults
        pass
    
    # Fall back to hardcoded
    return DOCTYPE_ALLOWED_FILTERS.get(doctype, ["name"])


def _get_valid_fields(doctype, meta):
    """Get list of all valid field names for a doctype"""
    return [f.fieldname for f in meta.fields] + DEFAULT_COLUMNS


# For listview get request only
def setup_request_data(
    doctype: str,
    user_filters: list = [],
    force_user_filters: bool = False,
) -> tuple:
    """
    Setup and validate request data for list queries
    
    Processes request parameters to build validated filters, pagination, and sorting
    for database queries. Supports advanced filtering with operators and multiple sort fields.
    
    Args:
        doctype: The DocType to query
        user_filters: Additional filters to apply (list of [field, operator, value])
        force_user_filters: If True, user_filters override request filters for same fields
    
    Returns:
        tuple: (page, page_length, order_by, filters, or_filters)
            - page (int): Page number (0-indexed)
            - page_length (int): Number of records per page (max 1000)
            - order_by (str): SQL ORDER BY clause
            - filters (list): List of AND filters [[field, operator, value], ...]
            - or_filters (list): List of OR filters for search [[field, "like", value], ...]
    
    Request Parameters:
        - page (int): Page number (1-indexed, max 10000)
        - limit (int): Records per page (max 1000, default 20)
        - order_by (str): Sort field(s) and direction
            Examples: "name asc", "department asc, name desc"
        - q (str): Search query (searches across search_fields)
        - {field_name} (any): Filter by exact field value
        - {field_name}_{operator} (any): Filter with operator
            Operators: _eq, _ne, _gt, _gte, _lt, _lte, _like, _in
            Examples: from_date_gte=2025-01-01, status_ne=Cancelled
    
    Examples:
        >>> # Simple pagination
        >>> GET /api/v1/employee/list?page=2&limit=50
        
        >>> # Date range filter
        >>> GET /api/v1/leave/list?from_date_gte=2025-01-01&to_date_lte=2025-12-31
        
        >>> # Multiple sort fields
        >>> GET /api/v1/employee/list?order_by=department asc, name desc
        
        >>> # Search with filters
        >>> GET /api/v1/employee/list?q=john&department=Sales
    
    Raises:
        frappe.ValidationError: If page or limit exceeds maximum allowed values
    """
    page = 0
    page_length = DEFAULT_PAGE_LENGTH
    order_by = "modified desc"
    filters = []

    allowed_filters = get_allowed_filters(doctype)
    
    # Validate and sanitize page number
    if "page" in frappe.request.args:
        page = cint(frappe.request.args["page"]) - 1
        if page < 0:
            page = 0
        elif page > MAX_PAGE_NUMBER:
            frappe.throw(
                _("Page number too large. Maximum allowed is {0}").format(MAX_PAGE_NUMBER)
            )
    
    # Validate and sanitize page length
    if "limit" in frappe.request.args:
        page_length = cint(frappe.request.args["limit"])
        if page_length <= 0:
            page_length = DEFAULT_PAGE_LENGTH
        elif page_length > MAX_PAGE_LENGTH:
            frappe.throw(
                _("Page length too large. Maximum allowed is {0}").format(MAX_PAGE_LENGTH)
            )
    
    
    # Validate and sanitize order_by to prevent SQL injection
    # Now supports multiple sort fields: "department asc, name desc"
    if "order_by" in frappe.request.args:
        order_by = parse_order_by(
            cstr(frappe.request.args["order_by"]),
            allowed_filters
        )

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
    """
    Get valid filters from request parameters
    
    Args:
        doctype: DocType name
        meta: DocType meta object
        user_filters: List of user-defined filters
        force_user_filters: If True, skip request filters that conflict with user_filters
    
    Returns:
        list: List of filter tuples [field, operator, value]
    """
    user_filters_keys = [f[0] for f in user_filters]
    allowed_filters = get_allowed_filters(doctype)
    filters = []
    
    # Cache field metadata to avoid repeated meta.get_field() calls
    # This improves performance from O(n*m) to O(n) where n=filters, m=fields
    field_cache = {f.fieldname: f for f in meta.fields}
    
    # Process all request args to find filters with operators
    # Example: from_date_gte=2025-01-01 becomes ("from_date", ">=", "2025-01-01")
    for request_key in frappe.request.args:
        # Parse filter key to get actual field name and operator
        filter_key, operator = parse_filter_with_operator(request_key)
        
        # Skip if not in allowed filters
        if filter_key not in allowed_filters and filter_key not in DEFAULT_COLUMNS:
            continue
        
        # Skip if conflicts with user_filters
        if filter_key in user_filters_keys and force_user_filters:
            continue
        
        value = cstr(frappe.request.args[request_key])
        if value is None or not value:
            continue

        if filter_key not in DEFAULT_COLUMNS:
            # Use cached field instead of meta.get_field() for better performance
            field = field_cache.get(filter_key)
            if not field:
                frappe.log_error(
                    f"Field '{filter_key}' not found in {doctype} meta",
                    "Request Data Validation"
                )
                continue
            
            field_type = field.fieldtype
            if field_type in DATA_FIELDS:
                if len(value) > 0:
                    filters.append([filter_key, operator, value])
            elif field_type == "Date":
                try:
                    value = getdate(value)
                    filters.append([filter_key, operator, value])
                except ParserError as e:
                    frappe.log_error(
                        f"Invalid date value '{value}' for filter '{filter_key}' in {doctype}: {str(e)}",
                        "Filter Validation Error"
                    )
            elif field_type == "Datetime":
                try:
                    value = get_datetime(value)
                    # Use 'like' for default operator, otherwise use specified operator
                    if operator == "=":
                        filters.append([filter_key, "like", f"%{value}%"])
                    else:
                        filters.append([filter_key, operator, value])
                except ParserError as e:
                    frappe.log_error(
                        f"Invalid datetime value '{value}' for filter '{filter_key}' in {doctype}: {str(e)}",
                        "Filter Validation Error"
                    )
            elif field_type == "Time":
                try:
                    value = get_time(value)
                    filters.append([filter_key, operator, value])
                except ParserError as e:
                    frappe.log_error(
                        f"Invalid time value '{value}' for filter '{filter_key}' in {doctype}: {str(e)}",
                        "Filter Validation Error"
                    )
            elif field_type == "Int":
                value = cint(value)
                filters.append([filter_key, operator, value])
            elif field_type in FLOAT_NUMBER_FIELDS:
                value = flt(value)
                filters.append([filter_key, operator, value])
            elif field_type == "Check":
                if value.lower() == "yes":
                    filters.append([filter_key, "=", 1])
                elif value.lower() == "no":
                    filters.append([filter_key, "=", 0])
        else:
            if filter_key in ["name", "modified_by", "owner"]:
                if len(value) > 0:
                    filters.append([filter_key, operator, value])
            elif filter_key in ["creation", "modified"]:
                try:
                    value = get_datetime(value)
                    filters.append([filter_key, operator, value])
                except ParserError as e:
                    frappe.log_error(
                        f"Invalid datetime value '{value}' for filter '{filter_key}' in {doctype}: {str(e)}",
                        "Filter Validation Error"
                    )
            elif filter_key == "docstatus":
                value = cint(value)
                if value in [0, 1, 2]:
                    filters.append([filter_key, "=", value])
    filters += user_filters
    return filters


def add_custom_filters(doctype):
    """
    Get custom filters defined in DOCTYPE_ALLOWED_CUSTOM_FILTERS
    
    Args:
        doctype: DocType name
        
    Returns:
        list: List of custom filters
    """
    filters = []
    allowed_filters = DOCTYPE_ALLOWED_CUSTOM_FILTERS.get(doctype, [])
    filters += allowed_filters
    return filters


def add_search_params(doctype, meta):
    """
    Add search filters from 'q' parameter
    
    Args:
        doctype: DocType name
        meta: DocType meta object
    
    Returns:
        list: List of OR filters for search
    """
    filters = []
    search_fields = ["name"]
    
    # Optimized: Use list comprehension instead of map + lambda
    if meta.search_fields:
        search_fields += [f.strip() for f in meta.search_fields.split(",") if f.strip()]
    
    search_fields = set(search_fields)

    if "q" in frappe.request.args:
        value = cstr(frappe.request.args["q"]).strip()
        if len(value) > 0:
            for field in search_fields:
                filters.append([field, "like", f"%{value}%"])
    return filters
