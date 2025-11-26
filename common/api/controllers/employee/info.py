from frappe import _
from common.api.utils.response import (
    build_error_response,
    build_success_response,
)
from common.api.utils.endpoints import update_doc, get_doc

doctype = "Employee"


def update_employee_info(employee: str):
    only_for = [
        "cell_number",
        "personal_email",
        "current_address",
        "linkedin_profile_url",
    ]
    return update_doc(doctype, employee, only_for=only_for, ignore_perms=True)


def other_employee_info(employee: str):
    fields = [
        "name",
        "status",
        "employee_name",
        "image",
        "gender",
        "date_of_birth",
        "designation",
        "department",
        "cell_number",
        "linkedin_profile_url",
        "personal_email",
        "company_email",
        "current_address",
    ]

    try:
        doc = get_doc(
            doctype,
            employee,
            add_perms=False,
            add_wf=False,
            ignore_perms=True,
            fields=fields,
        )
        msg = _("{} data fetched").format(_(doctype))
        return build_success_response(200, msg, doc, {})
    except Exception as exc:
        http_status_code = 500
        message = exc
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 0 and isinstance(args[0], str):
                message = args[0].split(":")[0]
            elif len(args) > 1 and isinstance(args[0], int):
                message = args[1]
        msg = _("failed to read {}").format(_(doctype))
        return build_error_response(http_status_code, msg, message)


def employee_info(employee: str):
    try:
        doc = get_doc(
            doctype,
            employee,
            add_perms=False,
            add_wf=False,
            ignore_perms=False,
            fields=[],
        )
        msg = _("{} data fetched").format(_(doctype))
        return build_success_response(200, msg, doc, {})
    except Exception as exc:
        http_status_code = 500
        message = exc
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 0 and isinstance(args[0], str):
                message = args[0].split(":")[0]
            elif len(args) > 1 and isinstance(args[0], int):
                message = args[1]
        msg = _("failed to read {}").format(_(doctype))
        return build_error_response(http_status_code, msg, message)
