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
def achievement_list(employee: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Achievement"
    filters = {"employee": employee}

    LIST_FIELDS = [
        "name",
        "employee",
        "employee_name",
        "title",
        "date",
        "description",
        "attachment",
        "status",
        "docstatus",
    ]
    return document_list(
        doctype,
        LIST_FIELDS,
        force_fields=True,
        user_filters=filters,
        force_user_filters=True,
    )


def create_achievement(employee: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Achievement"
    default_data = {"employee": employee}
    return create_doc(doctype, default_data=default_data)


def update_achievement(employee: str, name: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Achievement"
    default_data = {"employee": employee}
    return update_doc(doctype, name, default_data=default_data)


def delete_achievement(employee: str, name: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Achievement"
    return delete_doc(doctype, name)


# Employee Certification
def certification_list(employee: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Certification"
    filters = {"employee": employee}
    LIST_FIELDS = [
        "name",
        "employee",
        "employee_name",
        "certificate_title",
        "issuing_organization",
        "date_of_issue",
        "attachment",
        "status",
        "docstatus",
    ]
    return document_list(
        doctype,
        LIST_FIELDS,
        force_fields=True,
        user_filters=filters,
        force_user_filters=True,
    )


def create_certification(employee: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Certification"
    default_data = {"employee": employee}
    return create_doc(doctype, default_data=default_data)


def update_certification(employee: str, name: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Certification"
    default_data = {"employee": employee}
    return update_doc(doctype, name, default_data=default_data)


def delete_certification(employee: str, name: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Certification"
    return delete_doc(doctype, name)


# Employee Checkin
def create_checkin(employee: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Checkin"
    default_data = {"employee": employee}
    return create_doc(doctype, default_data=default_data)


def check_in_out_list(employee: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Employee Checkin"
    filters = {"employee": employee}

    LIST_FIELDS = [
        "name",
        "employee",
        "employee_name",
        "log_type",
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
        user_filters=filters,
        force_user_filters=True,
    )


# Employee Attendance
def attendance_list(employee: str):
    read_doc("Employee", employee, ["name"], force_fields=True)
    if frappe.local.response["status"] == "failed":
        return
    doctype = "Attendance"
    filters = {"employee": employee}

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
        user_filters=filters,
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
