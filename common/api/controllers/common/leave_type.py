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


def leave_type_list():
    doctype = "Leave Type"
    return document_list(
        doctype, fields, translate_text=True, tr_field="leave_type_name"
    )


def read_leave_type(name: str):
    doctype = "Leave Type"
    return read_doc(doctype, name, origin_fields=fields)
