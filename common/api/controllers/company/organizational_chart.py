import frappe
from frappe import _
from common.api.controllers.company import build_department_tree, build_employee_tree
from common.api.utils.response import (
    build_success_response,
)


def employee_structure():
    company = None
    reports_to = None
    employee = None
    department = None
    search = None

    def split_csv(s):
        if not s:
            return None
        vals = [x.strip() for x in s.split(",") if x.strip()]
        return vals or None

    if "reports_to" in frappe.request.args:
        reports_to = frappe.request.args["reports_to"]
        reports_to = (
            split_csv(reports_to) if reports_to and "," in reports_to else reports_to,
        )
    if "employee" in frappe.request.args:
        employee = frappe.request.args["employee"]
        employee = (split_csv(employee) if employee and "," in employee else employee,)
    if "department" in frappe.request.args:
        department = frappe.request.args["department"]
        department = (
            split_csv(department) if department and "," in department else department,
        )
    if "company" in frappe.request.args:
        company = frappe.request.args["company"]
        company = (split_csv(company) if company and "," in company else company,)
    if "search" in frappe.request.args:
        search = frappe.request.args["search"]
    max_depth = 100
    include_inactive = False

    employees = build_employee_tree(
        reports_to=reports_to,
        department=department,
        employee_id=employee,
        company=company,
        include_inactive=include_inactive,
        max_depth=max_depth,
        search=search,
    )
    return build_success_response(200, _("Employee Structure"), employees)


def department_structure():
    company = None
    parent = None
    department = None
    search = None
    if "parent" in frappe.request.args:
        parent = frappe.request.args["parent"]
    if "department" in frappe.request.args:
        department = frappe.request.args["department"]
    if "company" in frappe.request.args:
        company = frappe.request.args["company"]
    if "search" in frappe.request.args:
        search = frappe.request.args["search"]
    departments = build_department_tree(
        parent=parent, company=company, search=search, department=department
    )
    return build_success_response(200, _("Department Structure"), departments)
