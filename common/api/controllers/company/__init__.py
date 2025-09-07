import frappe
from frappe.utils import cint

from common.api.controllers.company.organizational_chart import (
    get_employee_structure,
    get_department_structure,
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
    )


def read_event(name: str):
    doctype = "Event"
    return read_doc(doctype, name, origin_fields=FROM_FIELDS, force_fields=True)


def employee_structure():
    def build_organization_tree(parent=None, company=None, exclude_node=None):
        children = get_employee_structure(
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

    employees = build_organization_tree(parent=parent, company=company)
    return build_success_response(200, f"Employee Structure", employees)


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
    return build_success_response(200, f"Department Structure", departments)


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
        doctype, NEWS_LIST_FIELDS, force_fields=True, user_filters=filters
    )


def read_newsletter(name: str):
    doctype = "Company Newsletter"
    return read_doc(doctype, name, origin_fields=NEWS_FROM_FIELDS, force_fields=True)
