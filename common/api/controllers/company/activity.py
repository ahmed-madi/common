import frappe
from frappe import _
from frappe.utils import getdate
from frappe.query_builder.custom import ConstantColumn
from frappe.query_builder.functions import IfNull
from werkzeug.routing import Rule
from common.api.utils.resource import BaseResource
from common.api.utils.decorators import safe_api

class ActivityResource(BaseResource):
    doctype = "Activity" # Virtual
    url_prefix = "/company"
    resource_name = "activities"
    
    @classmethod
    def list(cls):
        @safe_api
        def _list():
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

            return response_data, _("Company activities fetched")
        
        _list.__name__ = "company_activities_list"
        return _list

    @classmethod
    def get_routes(cls):
        name = cls.resource_name
        base_url = f"{cls.url_prefix}/{name}"
        return [
            Rule(base_url, methods=["GET"], endpoint=cls.list())
        ]
