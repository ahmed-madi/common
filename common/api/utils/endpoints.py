import frappe
from frappe import _

from common.api.utils import (
    get_request_form_data,
    format_data,
    upload_file,
    delete_duplicated_or_after_error,
    sanitize_html,
)
from common.api.utils.request_data import setup_request_data
from common.api.utils.response_data import format_response_data

from common.api.utils.response import (
    build_error_response,
    build_success_response,
    handle_exception_response,
)


def load_extra_list_data(data, doctype):
    if not isinstance(data, list):
        return
    if doctype == "Notification Log":
        for d in data:
            email_content = sanitize_html(d.get("email_content", ""))
            d.update(
                {
                    "email_content": email_content,
                }
            )

    if doctype == "Company Newsletter":
        for d in data:
            images_gallery = frappe.get_all(
                "Image Attachment",
                filters={
                    "parent": d["name"],
                    "parentfield": "images_gallery",
                    "parenttype": doctype,
                },
                pluck="image",
            )
            d.update(
                {
                    "images_gallery": images_gallery,
                }
            )


def get_doc_list(
    doctype: str,
    fields: list | str | None,
    user_filters=[],
    force_user_filters=False,
    append_user_filters=False,
    add_perms=True,
    add_wf=True,
):
    group_by = None
    parent = None
    limit_start, limit_page_length, order_by, filters, or_filters = setup_request_data(
        doctype, user_filters, force_user_filters
    )
    if append_user_filters:
        filters += user_filters
    limit_start = limit_start * limit_page_length

    wf = None
    if add_wf:
        wf = frappe.get_all("Workflow", {"document_type": doctype, "is_active": 1})
        if wf:
            wf = frappe.get_doc("Workflow", wf[0])
        else:
            wf = None
    if wf:
        fields.append(wf.workflow_state_field)
    if "docstatus" not in fields:
        fields.append("docstatus")

    args = frappe._dict(
        parent_doctype=parent,
        fields=fields,
        filters=filters,
        or_filters=or_filters,
        group_by=group_by,
        order_by=order_by,
        limit_start=limit_start,
        limit_page_length=limit_page_length,
        as_list=False,
    )
    count = len(frappe.get_list(doctype, limit_page_length=999999999))
    data = frappe.call(frappe.client.get_list, doctype, **args)

    # load perms and workflows, translate link and select field
    data = format_response_data(doctype, data, add_perms=add_perms, wf=wf, add_wf=add_wf)
    response_data = frappe._dict()
    response_data.update(
        {
            "data_list": data,
            "doctype": {
                "label": _(doctype),
                "value": doctype,
            },
            "meta": "",
            "page": limit_start + 1,
            "perPage": limit_page_length,
            "totalCount": count,
            "pageCount": len(data),
        }
    )
    return response_data


def document_list(
    doctype: str,
    fields: list | str,
    user_filters=[],
    force_user_filters=False,
    append_user_filters=False,
    add_perms=True,
    add_wf=True,
):
    try:
        response_data = get_doc_list(
            doctype,
            fields=fields,
            user_filters=user_filters,
            force_user_filters=force_user_filters,
            append_user_filters=append_user_filters,
            add_perms=add_perms,
            add_wf=add_wf,
        )
        msg = _("{} data fetched").format(_(doctype))
        return build_success_response(200, msg, response_data)
    except Exception as exc:
        print(frappe.get_traceback())
        http_status_code = 500
        message = exc
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 1 and isinstance(args[0], int):
                message = args[1]
            elif len(args) > 0:
                message = args[0].split(":")[0]
        msg = _("failed to read {}").format(_(doctype))
        return build_error_response(
            http_status_code, f"failed to read {doctype}", message
        )


def create_doc(
    doctype: str,
    default_data={},
    add_perms=True,
    add_wf=True,
):
    uploaded_files = []
    doc = None
    try:
        data = get_request_form_data()
        if not isinstance(data, bytes):
            data.pop("doctype", None)
            data = format_data(data, doctype)
            doc = frappe.new_doc(doctype, **data)
        else:
            doc = frappe.new_doc(doctype)
        uploaded_files = handle_files(doc)
        for file in uploaded_files:
            fieldname = file.get("fieldname")
            doc.update(
                {
                    f"{fieldname}": file.get("file_url"),
                }
            )
        doc.update(default_data)
        doc.save()
        delete_duplicated_or_after_error(uploaded_files)
        msg = _("{} created").format(_(doctype))
        doc = get_doc(doctype, doc.name, add_perms=add_perms, add_wf=add_wf)
        return build_success_response(201, msg, doc)
    except Exception as exc:
        print(frappe.get_traceback())
        return handle_exception_response(
            doc, doctype, exc, uploaded_files=uploaded_files
        )


def handle_files(doc):
    meta = frappe.get_meta(doc.doctype)
    uploaded_files = []
    for field in meta.fields:
        if field.fieldtype not in ["Attach", "Attach Image"]:
            continue
        file_doc_name = upload_file(field.fieldname)
        if file_doc_name is not None:
            uploaded_files.append(file_doc_name)
    return uploaded_files


def load_extra_load_checkin_data(doctype, name):
    extra_data = {}
    if doctype != "Employee":
        return extra_data
    last_check_in = frappe.get_all(
        "Employee Checkin",
        filters={"employee": name},
        fields=["log_type", "time"],
        order_by="time desc",
    )
    if len(last_check_in):
        last_check_in = last_check_in[0]
    else:
        last_check_in = None
    extra_data.update({"checkin_status": last_check_in})
    return extra_data


def load_extra_data(doctype, name):
    extra_data = {}
    if doctype == "HR Ticket":
        comments = frappe.get_all(
            "HR Ticket Comment",
            filters={"hr_ticket": name},
            fields=[
                "name",
                "hr_ticket",
                "comment",
                "attachment",
                "parent_comment",
                "creation as created_at",
                "owner as created_by",
            ],
        )
        extra_data.update({"comments": comments})
    elif doctype == "Employee":
        certifications = frappe.db.sql(
            """
                            SELECT name, employee, employee_name, certificate_title, issuing_organization,
                                    date_of_issue, attachment
                            FROM `tabEmployee Certification`
                            WHERE employee='{}'""".format(name),
            as_dict=True,
        )
        achievements = frappe.db.sql(
            """
                            SELECT name, employee, employee_name, title, date, description,
                                    attachment
                            FROM `tabEmployee Achievement`
                            WHERE employee='{}'""".format(name),
            as_dict=True,
        )

        last_salary_structure_assignment = {}
        last_salary_structure = {}
        last_salary_slip_based_on_last_salary_structure = {}
        last_salary_slip = {}

        assignments = frappe.get_all(
            "Salary Structure Assignment",
            filters={"employee": name, "docstatus": 1},
            fields=["*"],
            order_by="from_date",
        )
        salary_slip = frappe.get_all(
            "Salary Slip",
            filters={"employee": name, "docstatus": 1},
            fields=["name", "salary_structure"],
            order_by="start_date",
        )
        if len(salary_slip) > 0:
            last_salary_slip = frappe.get_doc("Salary Slip", salary_slip[0].name)

        if len(assignments) > 0:
            last_salary_structure_assignment = assignments[0]
            last_salary_structure = frappe.get_doc(
                "Salary Structure", last_salary_structure_assignment.salary_structure
            )
            for slip in salary_slip:
                if (
                    slip.salary_structure
                    != last_salary_structure_assignment.salary_structure
                ):
                    continue
                last_salary_slip_based_on_last_salary_structure = frappe.get_doc(
                    "Salary Slip", slip.name
                )
                break
        custodies = frappe.db.sql(
            """
                            SELECT *
                            FROM `tabAsset`
                            WHERE docstatus=1 AND custodian='{}'""".format(name),
            as_dict=True,
        )

        extra_data.update(
            {
                "certifications": certifications,
                "achievements": achievements,
                "last_salary_structure_assignment": last_salary_structure_assignment,
                "last_salary_structure": last_salary_structure,
                "last_salary_slip_based_on_last_salary_structure": last_salary_slip_based_on_last_salary_structure,
                "last_salary_slip": last_salary_slip,
                "custodies": custodies,
            }
        )
        extra_data.update(load_extra_load_checkin_data(doctype, name))
    return extra_data


def add_check_data(name):
    extra_data = {}
    last_check_in = frappe.get_all(
        "Employee Checkin",
        filters={"employee": name},
        fields=["log_type", "time"],
        order_by="time desc",
    )
    if len(last_check_in):
        last_check_in = last_check_in[0]
    else:
        last_check_in = None
    extra_data.update({"checkin_status": last_check_in})
    return extra_data


def get_doc(
    doctype: str,
    name: str,
    add_perms=True,
    add_wf=True,
    ignore_perms=False,
    fields=[],
):
    print(ignore_perms, doctype)
    print(ignore_perms, doctype)
    print(ignore_perms, doctype)
    print(ignore_perms, doctype)
    doc = frappe.get_doc(doctype, name)
    if not ignore_perms and not doc.has_permission("read"):
        raise frappe.PermissionError
    doc.apply_fieldlevel_read_permissions()
    doc = doc.as_dict()
    if fields and ("name" not in fields):
        fields.append("name")
    wf = None
    if add_wf:
        wf = frappe.get_all("Workflow", {"document_type": doctype, "is_active": 1})
        if wf:
            wf = frappe.get_doc("Workflow", wf[0])
            if fields:
                fields.append(wf.workflow_state_field)
        else:
            wf = None
    doc = format_response_data(
        doctype, [doc], add_perms=add_perms, wf=wf, reqd_field=fields
    )[0]
    if doctype == "Employee":
        doc.update(add_check_data(name))
    return doc


def read_doc(
    doctype: str,
    name: str,
    add_perms=True,
    add_wf=True,
    ignore_perms=False,
    fields=[],
):
    try:
        doc = get_doc(
            doctype,
            name,
            add_perms=add_perms,
            add_wf=add_wf,
            ignore_perms=ignore_perms,
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


def update_doc(
    doctype: str,
    name: str,
    ignore_perms=False,
    keys_to_update=[],
    add_perms=True,
    add_wf=True,
    only_for=[],
):
    uploaded_files = []
    doc = None
    try:
        data = get_request_form_data()
        doc = frappe.get_doc(doctype, {"name": name}, for_update=True)
        if not isinstance(data, bytes):
            if "flags" in data:
                del data["flags"]
            data = format_data(data, doctype, keys_to_update=keys_to_update)
            if len(only_for) > 0:
                new_data = {}
                for k in data:
                    if k not in only_for:
                        continue
                    new_data.update({k: data[k]})
            else:
                new_data = data
            doc.update(new_data)
        uploaded_files = handle_files(doc)
        for file in uploaded_files:
            fieldname = file.get("fieldname")
            doc.update(
                {
                    f"{fieldname}": file.get("file_url"),
                }
            )
        doc.save(ignore_permissions=ignore_perms)
        delete_duplicated_or_after_error(uploaded_files)
        # check for child table doctype
        if doc.get("parenttype"):
            frappe.get_doc(doc.parenttype, doc.parent).save()
        msg = _("{} updated").format(_(doctype))
        doc = get_doc(doctype, name, add_perms=add_perms, add_wf=add_wf)
        return build_success_response(200, msg, doc)
    except Exception as exc:
        return handle_exception_response(
            doc, doctype, exc, uploaded_files=uploaded_files, for_update=True
        )


def delete_doc(doctype: str, name: str):
    try:
        doc = frappe.delete_doc(doctype, name, ignore_missing=False)
        # frappe.response.http_status_code = 202
        msg = _("{} deleted").format(_(doctype))
        return build_success_response(202, msg, doc)
    except Exception as exc:
        return handle_exception_response(
            None, doctype, exc, uploaded_files=[], for_delete=True
        )


def handle_call(method: str):
    import frappe.handler

    method = method.split("/")[0]
    frappe.form_dict.cmd = method
    return frappe.handler.handle()
