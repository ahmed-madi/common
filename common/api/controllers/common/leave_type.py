from common.api.utils.resource import BaseResource

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
