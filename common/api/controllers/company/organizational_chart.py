# app_name/app_name/organization.py
from __future__ import annotations
from typing import Dict, List, Optional, Set, Any, Union, Iterable
import frappe

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

def _format_node(row: Dict[str, Any]) -> Dict[str, Any]:
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

def _detect_cycle(start: str, parent_map: Dict[str, Optional[str]]) -> Optional[List[str]]:
    seen: Set[str] = set()
    stack: Set[str] = set()

    def dfs(u: str) -> Optional[List[str]]:
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

def _normalize_filter_value(v: Optional[Union[str, List[str]]]) -> Optional[Union[str, List[str]]]:
    if not v:
        return None
    if isinstance(v, str):
        s = v.strip()
        return s or None
    if isinstance(v, list):
        vals = [str(x).strip() for x in v if str(x).strip()]
        return vals or None
    return None

def _split_terms(s: Optional[str | List[str]]) -> List[str]:
    if not s:
        return []
    if isinstance(s, list):
        parts = s
    else:
        parts = [p for chunk in s.split(",") for p in chunk.split(" ")]
    terms = [p.strip() for p in parts if p and p.strip()]
    seen = set()
    out = []
    for t in terms:
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out

def _batched(iterable: Iterable[str], n: int = 200) -> Iterable[List[str]]:
    batch: List[str] = []
    for x in iterable:
        batch.append(x)
        if len(batch) >= n:
            yield batch
            batch = []
    if batch:
        yield batch

def build_employee_tree(
    root: Optional[str] = None,
    include_inactive: bool = False,
    max_depth: int = 50,
    *,
    reports_to: Optional[Union[str, List[str]]] = None,
    department: Optional[Union[str, List[str]]] = None,
    employee_id: Optional[Union[str, List[str]]] = None,  # maps to Employee.name
    company: Optional[Union[str, List[str]]] = None,
    include_ancestors: bool = False,
    search: Optional[Union[str, List[str]]] = None,
) -> List[Dict[str, Any]]:
    """
    Build an org chart with optional filters, ancestor inclusion, and free-text search.

    Filters:
      - reports_to / department / employee_id / company: exact match (any-of if list)
      - search: OR 'like' across (employee_name, name, designation, department).

    Behavior:
      - Filtering occurs before tree assembly.
      - include_ancestors=True pulls missing manager chain(s) for matched rows,
        fetched without search/other filters (but still respecting include_inactive).
      - If a manager is excluded (by filters or inactive policy), the child becomes a root.
    """
    base_filters: Dict[str, Any] = {}
    if not include_inactive:
        base_filters["status"] = "Active"

    reports_to = _normalize_filter_value(reports_to)
    department = _normalize_filter_value(department)
    employee_id = _normalize_filter_value(employee_id)
    company = _normalize_filter_value(company)

    if reports_to:
        base_filters["reports_to"] = reports_to if isinstance(reports_to, str) else ("in", reports_to)
    if department:
        base_filters["department"] = department if isinstance(department, str) else ("in", department)
    if employee_id:
        base_filters["name"] = employee_id if isinstance(employee_id, str) else ("in", employee_id)
    if company:
        base_filters["company"] = company if isinstance(company, str) else ("in", company)

    # OR search across selected fields
    or_filters = []
    for term in _split_terms(search):
        like = f"%{term}%"
        or_filters.extend([
            ["employee_name", "like", like],
            ["name", "like", like],
            ["designation", "like", like],
            ["department", "like", like],
        ])

    rows = frappe.get_all("Employee",
                          fields=EMPLOYEE_FIELDS,
                          filters=base_filters,
                          or_filters=or_filters or None)

    if not rows:
        return []

    by_id: Dict[str, Dict[str, Any]] = {r["name"]: _format_node(r) for r in rows}
    parent_map: Dict[str, Optional[str]] = {r["name"]: r.get("reports_to") for r in rows}

    # Optionally bring in ancestors (manager chain), respecting include_inactive flag
    if include_ancestors:
        missing: Set[str] = set()
        for eid, parent in parent_map.items():
            p = parent
            while p and p not in by_id:
                missing.add(p)
                # We don't know this manager's parent yet; fetch later
                # (we'll discover their parent after we load the missing rows)
                break

        # Iteratively fetch up the chain until closure or safety cap
        hops = 0
        MAX_HOPS = 50
        while missing and hops < MAX_HOPS:
            # fetch a batch of missing managers
            fetch_filters = {"name": ("in", list(missing))}
            if not include_inactive:
                fetch_filters["status"] = "Active"

            new_rows = frappe.get_all("Employee", fields=EMPLOYEE_FIELDS, filters=fetch_filters)
            missing.clear()
            if not new_rows:
                break

            for r in new_rows:
                if r["name"] not in by_id:
                    by_id[r["name"]] = _format_node(r)
                    parent_map[r["name"]] = r.get("reports_to")

            # discover next layer of missing ancestors
            for eid, parent in list(parent_map.items()):
                if parent and parent not in by_id:
                    missing.add(parent)
            hops += 1

    # If parent isn't in our current set (filtered out / not found), treat as root
    for eid, parent in list(parent_map.items()):
        if parent and parent not in by_id:
            parent_map[eid] = None

    # Detect & break cycles for safety
    for eid in list(parent_map.keys()):
        cycle = _detect_cycle(eid, parent_map)
        if cycle:
            victim = cycle[0]
            parent_map[victim] = None
            if victim in by_id:
                by_id[victim]["reports_to"] = None

    # Build children lists
    for eid, parent in parent_map.items():
        if parent and parent in by_id and eid in by_id:
            by_id[parent]["children"].append(by_id[eid])

    # Choose roots
    if root:
        if root not in by_id:
            return []
        roots = [by_id[root]]
    else:
        roots = [node for eid, node in by_id.items() if not parent_map.get(eid)]

    # Depth guard
    def prune(node: Dict[str, Any], depth: int):
        if depth >= max_depth:
            node["children"] = []
            return
        for child in node["children"]:
            prune(child, depth + 1)

    for r in roots:
        prune(r, 1)

    # Stable sort for predictable UI
    def sort_rec(node: Dict[str, Any]):
        node["children"].sort(key=lambda n: (n["department"] or "", n["label"] or ""))
        for c in node["children"]:
            sort_rec(c)

    for r in roots:
        sort_rec(r)

    return roots

def get_department_structure(parent=None, company=None, exclude_node=None):
    filters = [["disabled", "=", 0]]
    # if not company or company is None:
    #     company = get_default_company()

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
