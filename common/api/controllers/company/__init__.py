import frappe
from frappe.utils import cint, getdate

from common.api.controllers.company.organizational_chart import (
    get_department_structure,
    build_employee_tree,
)


from common.api.utils.endpoints import document_list, read_doc
from common.api.utils.response import (
    build_success_response,
)

LIST_FIELDS = [
    "name",
    "subject",
    "published",
    "event_category",
    "color",
    "cover_image",
    "starts_on",
    "ends_on",
    "event_location",
    "status",
]
FROM_FIELDS = LIST_FIELDS + ["description"]


def event_list():
    doctype = "Event"

    filters = {}
    force_filters = False

    if cint(frappe.db.get_single_value("Company Policy", "active_event_only")) == 1:
        force_filters = True
        filters = {
            "status": "Open",
            "published": 1,
        }
    return document_list(
        doctype,
        LIST_FIELDS,
        force_fields=True,
        user_filters=filters,
        force_user_filters=force_filters,
        order_by="starts_on desc",
    )


def read_event(name: str):
    doctype = "Event"
    return read_doc(doctype, name, origin_fields=FROM_FIELDS, force_fields=True)


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
    return build_success_response(200, "Employee Structure", employees)


def department_structure():
    def build_organization_tree(parent=None, company=None, exclude_node=None):
        children = get_department_structure(
            parent=parent, company=company, exclude_node=exclude_node
        )
        if len(children) == 0:
            return []
        for child in children:
            child.update(
                {
                    "children": build_organization_tree(
                        parent=child.get("id"),
                        company=company,
                        exclude_node=exclude_node,
                    )
                }
            )
        return children

    company = None
    parent = None

    if "parent" in frappe.request.args:
        parent = frappe.request.args["parent"]
    if "company" in frappe.request.args:
        company = frappe.request.args["company"]

    departments = build_organization_tree(parent=parent, company=company)
    return build_success_response(200, "Department Structure", departments)


NEWS_LIST_FIELDS = [
    "name",
    "subject",
    "publish_on",
    "cover_image",
    "published",
    "cover_image",
    "intro_description",
    "list_image",
]
NEWS_FROM_FIELDS = NEWS_LIST_FIELDS + ["description"]


def newsletter_list():
    doctype = "Company Newsletter"
    filters = {
        "published": 1,
    }
    return document_list(
        doctype,
        NEWS_LIST_FIELDS,
        force_fields=True,
        user_filters=filters,
        order_by="publish_on desc",
    )


def read_newsletter(name: str):
    doctype = "Company Newsletter"
    return read_doc(doctype, name, origin_fields=NEWS_FROM_FIELDS, force_fields=True)


def activity_list():
    doctype = "Company Newsletter"
    filters = {
        "published": 1,
    }
    news = frappe.get_all(
        doctype, filters=filters, fields=["name", "subject", "publish_on as date"]
    )
    for n in news:
        n.update(
            {
                "doctype": doctype,
            }
        )
    doctype = "Event"
    filters = {
        "published": 1,
    }
    events = frappe.get_all(
        doctype,
        filters=filters,
        fields=[
            "name",
            "subject",
            "starts_on as date",
        ],
    )
    for n in events:
        n.update(
            {
                "doctype": doctype,
            }
        )
    doctype = "Project"
    projects = frappe.get_list(
        doctype,
        filters={"expected_start_date": ["!=", ""]},
        fields=[
            "name",
            "project_name as subject",
            "expected_start_date as date",
        ],
    )
    fprojects = []
    for n in projects:
        if not n.date:
            continue
        n.update(
            {
                "doctype": doctype,
            }
        )
        fprojects.append(n)

    response_data = news + events + fprojects
    response_data.sort(key=lambda x: getdate(f"{x.date}".split(" ")[0]), reverse=True)

    return build_success_response(200, "Company activities fetched", response_data)
