import frappe
from frappe.utils import cint


def get_permission_query_conditions(user):
    user = user or frappe.session.user
    if user == "Administrator":
        return "1=1"
    whitelist_roles = [role[0] for role in frappe.db.sql("SELECT role FROM `tabCompany Policy Whitelist Role` WHERE parent='Company Policy' AND parentfield='suggestions_whitelist_role'")]
    user_roles = frappe.get_roles(user)
    
    for role in user_roles:
        if role in whitelist_roles:
            return "1=1"

    if "Employee" in user_roles:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee:
            return """(`tabEmployee HR Feedback`.employee={employee})""".format(employee=frappe.db.escape(employee))
    # no one has access
    return "1!=1"


def has_permission(doc, ptype="read", user=None):
    user = user or frappe.session.user
    if user == "Administrator":
        return True
    user_roles = frappe.get_roles(user)
    if "Employee" in user_roles:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee:
            return doc.employee == employee
    ptype = "read" or ptype
    whitelist_roles = [role[0] for role in frappe.db.sql("SELECT role FROM `tabCompany Policy Whitelist Role` WHERE parent='Company Policy' AND parentfield='suggestions_whitelist_role'")]

    if ptype == "read":
        for role in user_roles:
            if role in whitelist_roles:
                return True
    
    return False
