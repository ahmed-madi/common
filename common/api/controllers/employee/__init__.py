import frappe
from common.api.utils.endpoints import (
    document_list,
    create_doc,
    update_doc,
    delete_doc,
    read_doc,
)


# Employee
def employee_info(employee: str):
    doctype = "Employee"
    return read_doc(doctype, employee, load_checkin=True)


def update_employee_info(employee: str):
    doctype = "Employee"
    only_for = [
        "cell_number",
        "personal_email",
        "current_address",
        "linkedin_profile_url",
    ]
    return update_doc(doctype, employee, keys_to_update=only_for, ignore_perms=True)


# Employee Achievement
def achievement_list():
    doctype = "Employee Achievement"
    LIST_FIELDS = [
        "name",
        "employee",
        "employee_name",
        "title",
        "date",
        "description",
        "attachment",
    ]
    return document_list(
        doctype,
        LIST_FIELDS,
        force_fields=True,
        force_user_filters=True,
    )


def create_achievement():
    doctype = "Employee Achievement"
    return create_doc(doctype)


def update_achievement(name: str):
    doctype = "Employee Achievement"
    return update_doc(doctype, name)


def delete_achievement(name: str):
    doctype = "Employee Achievement"
    return delete_doc(doctype, name)


# Employee Certification
def certification_list():
    doctype = "Employee Certification"
    LIST_FIELDS = [
        "name",
        "employee",
        "employee_name",
        "certificate_title",
        "issuing_organization",
        "date_of_issue",
        "attachment",
    ]
    return document_list(
        doctype,
        LIST_FIELDS,
        force_fields=True,
        force_user_filters=True,
    )

def create_certification():
    doctype = "Employee Certification"
    return create_doc(doctype)


def update_certification(name: str):
    doctype = "Employee Certification"
    return update_doc(doctype, name)


def delete_certification(name: str):
    doctype = "Employee Certification"
    return delete_doc(doctype, name)

# Employee Checkin
def create_checkin():
    doctype = "Employee Checkin"
    return create_doc(doctype)


def check_in_out_list():
    doctype = "Employee Checkin"
    LIST_FIELDS = [
        "name",
        "employee",
        "employee_name",
        "log_type",
        "location_name",
        "shift",
        "time",
        "device_id",
        "attendance",
        "skip_auto_attendance",
        "latitude",
        "longitude",
        "shift_start",
        "shift_end",
        "offshift",
        "shift_actual_start",
        "shift_actual_end",
    ]
    return document_list(
        doctype,
        LIST_FIELDS,
        force_fields=True,
        force_user_filters=True,
    )


# Employee Attendance
def attendance_list():
    doctype = "Attendance"
    LIST_FIELDS = [
        "name",
        "employee",
        "employee_name",
        "working_hours",
        "status",
        "leave_type",
        "leave_application",
        "attendance_date",
        "department",
        "attendance_request",
        "shift",
        "in_time",
        "out_time",
        "late_entry",
        "early_exit",
        "docstatus",
    ]
    return document_list(
        doctype,
        LIST_FIELDS,
        force_fields=True,
        force_user_filters=True,
    )


def other_employee_info(employee: str):
    return read_doc(
        "Employee",
        employee,
        [
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
        ],
        force_fields=True,
        ignore_perms=True,
        load_extra_docs=False,
        load_checkin=True,
    )


def download_salary_slip(employee: str, name: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    from frappe.utils.print_format import download_pdf

    return download_pdf(doctype="Salary Slip", name=name)
