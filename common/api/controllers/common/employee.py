from werkzeug.routing import Rule
import frappe
from frappe import _
from frappe.utils import getdate, cint
from common.api.utils.resource import BaseResource
from common.api.utils.decorators import safe_api


class EmployeeResource(BaseResource):
    doctype = "Employee"
    fields = [
        "name",
        "image",
        "employee_name",
        "department",
        "designation",
        "date_of_joining",
    ]

    @classmethod
    def leave_balance_action(cls):
        @safe_api
        def _action(name):
            for_annual: int = frappe.request.values.get("for_annual", 1)

            # Logic extracted from previous function
            if not name:
                name = frappe.db.get_value(
                    "Employee", {"user_id": frappe.session.user}, "name"
                )

            if not name:
                frappe.throw(
                    _("Employee ID (name) must be provided"), frappe.MandatoryError
                )

            if not frappe.db.exists("Employee", name):
                frappe.throw(
                    _("The requested employee could not be found"),
                    frappe.DoesNotExistError,
                )

            employee = frappe.get_doc("Employee", name)
            if not frappe.has_permission(
                "Employee", "read", employee, frappe.session.user, False
            ):
                raise frappe.PermissionError(
                    _("You do not have permission to access employee details")
                )

            from hrms.hr.doctype.leave_application.leave_application import (
                get_leave_details,
            )

            date = getdate()
            leave_map = []
            leave_details = get_leave_details(employee.name, date)
            allocation = leave_details["leave_allocation"]

            if cint(for_annual) == 1:
                annual_leave = frappe.db.get_single_value(
                    "Company Policy", "annual_leave_type"
                )
                if not annual_leave:
                    frappe.throw(
                        _("Data for Annual Leave Type is not available"),
                        frappe.DoesNotExistError,
                    )

                details = allocation.get(annual_leave, {})
                leave_map.append(
                    {
                        "leave_type_name": annual_leave,
                        "leave_type_label": _(annual_leave),
                        "allocated_leaves": details.get("total_leaves", 0.0),
                        "balance_leaves": details.get("remaining_leaves", 0.0),
                        "expired_leaves": details.get("expired_leaves", 0.0),
                        "leaves_pending_approval": details.get(
                            "leaves_pending_approval", 0.0
                        ),
                    }
                )
                return leave_map, "Employee Annual Leave Balance Details"

            for leave_type, details in allocation.items():
                leave_map.append(
                    {
                        "leave_type_name": leave_type,
                        "leave_type_label": _(leave_type),
                        "allocated_leaves": details.get("total_leaves", 0.0),
                        "balance_leaves": details.get("remaining_leaves", 0.0),
                        "expired_leaves": details.get("expired_leaves", 0.0),
                        "leaves_pending_approval": details.get(
                            "leaves_pending_approval", 0.0
                        ),
                    }
                )
            return leave_map, "Employee Leave Balance Details"

        return _action

    @classmethod
    def get_routes(cls):
        routes = super().get_routes()
        name = cls.resource_name or cls.doctype.lower().replace(" ", "-")
        base_url = f"{cls.url_prefix}/{name}"

        # Add custom route
        routes.append(
            Rule(
                f"{base_url}/<path:name>/leave-balance",
                methods=["GET"],
                endpoint=cls.leave_balance_action(),
            )
        )
        return routes
