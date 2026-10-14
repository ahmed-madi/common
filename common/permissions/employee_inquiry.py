"""Who can access an Employee Inquiry.

- Users holding one of the company's `inquiry_full_access_roles` (Company
  Policy) see every inquiry of that company's employees.
- The employee of the inquiry sees it.
- The manager of the inquiry's management area (Department) sees it once it
  is no longer a draft.
"""

import frappe


def _full_access_companies(user):
    """Companies whose Company Policy grants this user full access."""
    return frappe.get_all(
        "Company Policy Whitelist Role",
        filters={
            "parenttype": "Company Policy",
            "parentfield": "inquiry_full_access_roles",
            "role": ("in", frappe.get_roles(user)),
        },
        pluck="parent",
        distinct=True,
    )


def _get_employee(user):
    return frappe.db.get_value("Employee", {"user_id": user}, "name")


def _managed_departments(employee):
    return frappe.get_all(
        "Department", filters={"department_manager": employee}, pluck="name"
    )


def _in_list(values):
    return ", ".join(frappe.db.escape(v) for v in values)


def get_permission_query_conditions(user):
    user = user or frappe.session.user
    if user == "Administrator":
        return ""

    conditions = []
    companies = _full_access_companies(user)
    if companies:
        conditions.append(
            "`tabEmployee Inquiry`.employee in (select name from `tabEmployee` where company in ({}))".format(
                _in_list(companies)
            )
        )

    employee = _get_employee(user)
    if employee:
        conditions.append(
            f"`tabEmployee Inquiry`.employee = {frappe.db.escape(employee)}"
        )
        departments = _managed_departments(employee)
        if departments:
            # managers only see non-draft inquiries of their management area
            conditions.append(
                "(`tabEmployee Inquiry`.docstatus != 0 and `tabEmployee Inquiry`.management_area in ({}))".format(
                    _in_list(departments)
                )
            )

    if not conditions:
        return "1=0"
    return "({})".format(" or ".join(conditions))


def has_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if user == "Administrator":
        return True

    companies = _full_access_companies(user)
    if companies and doc.employee:
        if frappe.db.get_value("Employee", doc.employee, "company") in companies:
            return True

    employee = _get_employee(user)
    if not employee:
        return False
    if doc.employee == employee:
        return True
    return (
        doc.docstatus != 0
        and bool(doc.management_area)
        and doc.management_area in _managed_departments(employee)
    )
