import frappe
from frappe import _
from frappe.utils import getdate
from frappe.query_builder.custom import ConstantColumn
from frappe.query_builder.functions import IfNull
from common.api.utils.response import (
    build_success_response,
)


def activity_list():
    Newsletter = frappe.qb.DocType("Company Newsletter")
    letters = (
        frappe.qb.from_(Newsletter)
        .select(
            Newsletter.name,
            Newsletter.subject,
            Newsletter.publish_on.as_("date"),
            ConstantColumn("Company Newsletter").as_("doctype"),
        )
        .where(Newsletter.published == 1)
        .run(as_dict=True)
    )

    Event = frappe.qb.DocType("Event")
    events = (
        frappe.qb.from_(Event)
        .select(
            Event.name,
            Event.subject,
            Event.starts_on.as_("date"),
            ConstantColumn("Event").as_("doctype"),
        )
        .where(Event.published == 1)
        .run(as_dict=True)
    )

    Project = frappe.qb.DocType("Project")
    projects = (
        frappe.qb.from_(Project)
        .select(
            Project.name,
            Project.project_name.as_("subject"),
            IfNull(Project.expected_start_date, "").as_("date"),
            ConstantColumn("Project").as_("doctype"),
        )
        .where(IfNull(Project.expected_start_date, "") != "")
        .run(as_dict=True)
    )

    response_data = letters + events + projects
    response_data.sort(key=lambda x: getdate(f"{x.date}".split(" ")[0]), reverse=True)

    return build_success_response(200, _("Company activities fetched"), response_data)
