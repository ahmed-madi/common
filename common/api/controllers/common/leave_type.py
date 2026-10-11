import frappe
from common.api.utils.resource import BaseResource
from frappe.utils import getdate, today
from hrms.hr.doctype.leave_application.leave_application import get_leave_details


class LeaveTypeResource(BaseResource):
    doctype = "Leave Type"
    fields = [
        "name",
        "leave_type_name",
        "max_leaves_allowed",
        "applicable_after",
        "max_continuous_days_allowed",
        "attachment_required",
        "reason_required",
        "is_carry_forward",
        "is_lwp",
        "allow_over_allocation",
        "is_compensatory",
    ]

    @classmethod
    def get_list_filters(cls):
        """Limit leave types to the ones the employee can apply for.

        When `employee` is passed, mirror the Leave Application form: only leave
        types with an active allocation on `date` (default today), plus LWP types.
        """
        filters = cls.list_user_filters.copy()
        employee = frappe.request.args.get("employee")
        if not employee:
            return filters

        date = getdate(frappe.request.args.get("date") or today())
        details = get_leave_details(employee, date)
        allowed = list(details["leave_allocation"]) + details["lwps"]
        # [""] keeps the IN clause valid when nothing is allowed
        return [["name", "in", allowed or [""]]] + filters
