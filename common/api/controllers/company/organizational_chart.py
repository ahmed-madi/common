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
    if isinstance(v, list) or isinstance(v, tuple):
        vals = [str(x).strip() for x in v if str(x).strip()]
        return vals or None
    return None

def _split_terms(s: Optional[str | List[str]]) -> List[str]:
    s = _normalize_filter_value(s)
    if not s:
        return []
    if isinstance(s, list) or isinstance(s, tuple):
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

def build_employee_tree(
    root: Optional[str] = None,
    include_inactive: bool = False,
    max_depth: int = 50,
    *,
    reports_to: Optional[Union[str, List[str]]] = None,
    department: Optional[Union[str, List[str]]] = None,
    employee_id: Optional[Union[str, List[str]]] = None,
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

    if include_ancestors:
        missing: Set[str] = set()
        for eid, parent in parent_map.items():
            p = parent
            while p and p not in by_id:
                missing.add(p)
                break

        hops = 0
        MAX_HOPS = 50
        while missing and hops < MAX_HOPS:
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

            for eid, parent in list(parent_map.items()):
                if parent and parent not in by_id:
                    missing.add(parent)
            hops += 1

    for eid, parent in list(parent_map.items()):
        if parent and parent not in by_id:
            parent_map[eid] = None

    for eid in list(parent_map.keys()):
        cycle = _detect_cycle(eid, parent_map)
        if cycle:
            victim = cycle[0]
            parent_map[victim] = None
            if victim in by_id:
                by_id[victim]["reports_to"] = None

    for eid, parent in parent_map.items():
        if parent and parent in by_id and eid in by_id:
            by_id[parent]["children"].append(by_id[eid])

    if root:
        if root not in by_id:
            return []
        roots = [by_id[root]]
    else:
        roots = [node for eid, node in by_id.items() if not parent_map.get(eid)]

    def prune(node: Dict[str, Any], depth: int):
        if depth >= max_depth:
            node["children"] = []
            return
        for child in node["children"]:
            prune(child, depth + 1)

    for r in roots:
        prune(r, 1)

    def sort_rec(node: Dict[str, Any]):
        node["children"].sort(key=lambda n: (n["department"] or "", n["label"] or ""))
        for c in node["children"]:
            sort_rec(c)

    for r in roots:
        sort_rec(r)

    return roots

DEPT_FIELDS = [
    "name",
    "department_name",
    "parent_department",
    "company",
    "is_group",
]

EMP_COUNT_FIELD = "count(name) as cnt"

def _fmt_dept(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row["name"],
        "label": row.get("department_name") or row["name"],
        "parent": row.get("parent_department"),
        "company": row.get("company"),
        "is_group": row.get("is_group"),
        "direct_count": 0,
        "total_count": 0,
        "children": [],
    }

def _stable_sort(node: Dict[str, Any]) -> None:
    node["children"].sort(key=lambda n: (n["label"] or "", n["id"]))
    for c in node["children"]:
        _stable_sort(c)

def _post_order_total(node: Dict[str, Any]) -> int:
    total = node["direct_count"]
    for c in node["children"]:
        total += _post_order_total(c)
    node["total_count"] = total
    return total

def build_department_tree(
    *,
    company: Optional[Union[str, List[str]]] = None,
    parent: Optional[Union[str, List[str]]] = None,
    department: Optional[Union[str, List[str]]] = None,
    include_inactive_employees: bool = False,
    include_ancestors: bool = True,
    search: Optional[str] = None,
    recursive_counts: bool = True,
    include_empty_departments: bool = True,
) -> List[Dict[str, Any]]:
    """
    Build a Department tree with employee counts.

    Filters (exact):
      - company: Department.company and Employee.company
      - parent: Department.parent_department
      - department: Department.name (IDs)
    search: OR-like across (department_name, name)
    """
    dept_filters: Dict[str, Any] = {}

    def _normalize(value: Optional[Union[str, List[str]]], field: str):
        if not value:
            return
        if isinstance(value, list):
            vals = [str(x).strip() for x in value if str(x).strip()]
            if vals:
                dept_filters[field] = ("in", vals)
        else:
            s = str(value).strip()
            if s:
                dept_filters[field] = s

    _normalize(company, "company")
    _normalize(parent, "parent_department")
    _normalize(department, "name")

    or_filters = []
    for term in _split_terms(search):
        like = f"%{term}%"
        or_filters.extend([
            ["department_name", "like", like],
            ["name", "like", like],
        ])

    dept_rows = frappe.get_all(
        "Department",
        fields=DEPT_FIELDS,
        filters=dept_filters,
        or_filters=or_filters or None
    )
    if not dept_rows:
        return []

    all_map: Dict[str, Dict[str, Any]] = {
        r["name"]: _fmt_dept(r) for r in dept_rows
    }

    if include_ancestors:
        missing: Set[str] = set()
        for d in list(all_map.values()):
            if d["parent"] and d["parent"] not in all_map:
                missing.add(d["parent"])

        hops = 0
        while missing and hops < 50:
            to_fetch = list(missing)
            missing.clear()
            anc_filters: Dict[str, Any] = {"name": ("in", to_fetch)}
            if company:
                if isinstance(company, list):
                    anc_filters["company"] = ("in", company)
                else:
                    anc_filters["company"] = company

            anc_rows = frappe.get_all("Department", fields=DEPT_FIELDS, filters=anc_filters)
            for r in anc_rows:
                if r["name"] not in all_map:
                    all_map[r["name"]] = _fmt_dept(r)

            for d in list(all_map.values()):
                if d["parent"] and d["parent"] not in all_map:
                    missing.add(d["parent"])
            hops += 1

    emp_filters: Dict[str, Any] = {}
    if not include_inactive_employees:
        emp_filters["status"] = "Active"
    if company:
        emp_filters["company"] = ("in", company) if isinstance(company, list) else company

    emp_counts = frappe.get_all(
        "Employee",
        fields=["department", EMP_COUNT_FIELD],
        filters=emp_filters,
        group_by="department"
    )

    for r in emp_counts:
        dept_id = r.get("department")
        if dept_id and dept_id in all_map:
            all_map[dept_id]["direct_count"] = int(r.get("cnt") or 0)

    parent_map: Dict[str, Optional[str]] = {d["id"]: d["parent"] for d in all_map.values()}
    for d in all_map.values():
        p = d["parent"]
        if p and p in all_map:
            all_map[p]["children"].append(d)

    roots = [d for d in all_map.values() if not parent_map.get(d["id"]) or parent_map.get(d["id"]) not in all_map]

    if recursive_counts:
        for r in roots:
            _post_order_total(r)
    else:
        for d in all_map.values():
            d["total_count"] = d["direct_count"]

    if not include_empty_departments:
        def prune_empty(node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            kept = []
            for c in node["children"]:
                pc = prune_empty(c)
                if pc:
                    kept.append(pc)
            node["children"] = kept
            if node["total_count"] == 0 and not kept:
                return None
            return node

        roots = [n for n in (prune_empty(r) for r in roots) if n]

    for r in roots:
        _stable_sort(r)

    return roots
