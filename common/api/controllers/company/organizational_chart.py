import frappe
from erpnext import get_default_company

def get_department_structure(parent=None, company=None, exclude_node=None):
    filters = [["disabled", "=", 0]]
    if not company or company is None:
        company = get_default_company()

    if company and company != "All Companies":
        filters.append(["company", "=", company])
    if parent and company and parent != company:
        filters.append(["parent_department", "=", parent])

    if exclude_node:
        filters.append(["name", "!=", exclude_node])

    departments = frappe.get_all(
        "Department",
        fields=[
            "department_name as name",
            "name as id",
            "lft",
            "rgt",
            "parent_department",
        ],
        filters=filters,
        order_by="name",
    )

    return departments

EMPLOYEE_FIELDS = [
    "name",
    "employee_name",
    "reports_to",
    "designation",
    "department",
    "company",
    "status",
    "image",
]

def _format_node(row):
    return {
        "id": row["name"],
        "label": row.get("employee_name") or row["name"],
        "reports_to": row.get("reports_to"),
        "designation": row.get("designation"),
        "department": row.get("department"),
        "company": row.get("company"),
        "status": row.get("status"),
        "image": row.get("image"),
        "children": [],
    }

def _detect_cycle(start, parent_map):
    seen = set()
    stack = set()

    def dfs(u):
        if u in stack:
            return [u]
        if u in seen:
            return None
        seen.add(u)
        stack.add(u)
        v = parent_map.get(u)
        if v:
            path = dfs(v)
            if path is not None:
                if path[0] == u:
                    return path
                path.append(u)
                return path
        stack.remove(u)
        return None

    return dfs(start)

def _normalize_filter_value(v):
    if not v:
        return None
    if isinstance(v, str):
        s = v.strip()
        return s or None
    if isinstance(v, list):
        vals = [str(x).strip() for x in v if str(x).strip()]
        return vals or None
    return None

def build_employee_tree(
    root = None,
    include_inactive = False,
    max_depth = 50,
    *,
    reports_to = None,
    department = None,
    employee_id = None,
    company = None,
):
    filters = {}
    if not include_inactive:
        filters["status"] = "Active"

    reports_to = _normalize_filter_value(reports_to)
    department = _normalize_filter_value(department)
    employee_id = _normalize_filter_value(employee_id)
    company = _normalize_filter_value(company)

    if reports_to:
        filters["reports_to"] = reports_to if isinstance(reports_to, str) else ("in", reports_to)
    if department:
        filters["department"] = department if isinstance(department, str) else ("in", department)
    if employee_id:
        filters["name"] = employee_id if isinstance(employee_id, str) else ("in", employee_id)
    if company:
        filters["company"] = company if isinstance(company, str) else ("in", company)

    rows = frappe.get_all("Employee", fields=EMPLOYEE_FIELDS, filters=filters)
    if not rows:
        return []

    by_id = {r["name"]: _format_node(r) for r in rows}
    parent_map = {r["name"]: r.get("reports_to") for r in rows}

    for eid, parent in list(parent_map.items()):
        if parent and parent not in by_id:
            parent_map[eid] = None

    for eid in list(parent_map.keys()):
        cycle = _detect_cycle(eid, parent_map)
        if cycle:
            victim = cycle[0]
            parent_map[victim] = None
            by_id[victim]["reports_to"] = None

    for eid, parent in parent_map.items():
        if parent:
            by_id[parent]["children"].append(by_id[eid])

    if root:
        if root not in by_id:
            return []
        roots = [by_id[root]]
    else:
        roots = [node for eid, node in by_id.items() if not parent_map.get(eid)]

    def prune(node, depth):
        if depth >= max_depth:
            node["children"] = []
            return
        for child in node["children"]:
            prune(child, depth + 1)

    for r in roots:
        prune(r, 1)

    def sort_rec(node):
        node["children"].sort(key=lambda n: (n["department"] or "", n["label"] or ""))
        for c in node["children"]:
            sort_rec(c)

    for r in roots:
        sort_rec(r)

    return roots
