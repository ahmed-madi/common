from common.api.utils.endpoints import document_list, read_doc

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
doctype = "Leave Type"


def leave_type_list():
    return document_list(
        doctype,
        fields,
        add_perms=False,
        add_wf=False,
    )


def read_leave_type(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
