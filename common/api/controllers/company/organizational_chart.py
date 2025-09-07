import frappe
from erpnext import get_default_company

# from hrms.hr.page.organizational_chart.organizational_chart import get_connections


def get_employee_structure(parent=None, company=None, exclude_node=None):
    filters = [["status", "=", "Active"]]
    if not company or company is None:
        company = get_default_company()

    if company and company != "All Companies":
        filters.append(["company", "=", company])

    if parent and company and parent != company:
        filters.append(["reports_to", "=", parent])
    else:
        filters.append(["reports_to", "=", ""])

    if exclude_node:
        filters.append(["name", "!=", exclude_node])

    employees = frappe.get_all(
        "Employee",
        fields=[
            "employee_name as name",
            "name as id",
            "lft",
            "rgt",
            "reports_to",
            "image",
            "designation as title",
            "company",
        ],
        filters=filters,
        order_by="name",
    )

    # for employee in employees:
    # 	employee.connections = get_connections(employee.id, employee.lft, employee.rgt)
    # 	employee.expandable = bool(employee.connections)

    return employees


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

    # for department in departments:
    # 	department.connections = get_connections(department.id, department.lft, department.rgt)
    # 	department.expandable = bool(department.connections)

    return departments
