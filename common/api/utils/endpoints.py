import frappe
from frappe import _
from frappe.utils import cint
from frappe.desk.form.load import get_docinfo #, getdoc, getdoctype

from common.api.utils import (
    get_request_form_data,
    format_data,
    upload_file,
    delete_duplicated_or_after_error,
)
from common.api.utils.response import (
    build_error_response,
    build_success_response,
    handle_exception_response,
)
from common.api.utils.translator import translate_link_fields

def load_extra_list_data(data, doctype):
    if not isinstance(data, list):
        return
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


def document_list(
    doctype: str,
    fields: list | str,
    force_fields=False,
    user_filters={},
    force_user_filters=False,
    order_by="modified desc",
    translate_text=False,
    tr_field=None,
):
    filters = {}
    or_filters = None
    group_by = None
    limit_start = 0
    limit_page_length = 20
    parent = None

    if not isinstance(user_filters, dict) or not not isinstance(user_filters, list):
        user_filters = {}

    try:
        if "limit_page_length" in frappe.request.args:
            limit_page_length = cint(frappe.request.args["limit_page_length"])
        if "limit" in frappe.request.args:
            limit_page_length = cint(frappe.request.args["limit"])

        if "limit_start" in frappe.request.args:
            limit_start = cint(frappe.request.args["limit_start"]) - 1
            if limit_start < 0:
                limit_start = 1
        if "page" in frappe.request.args:
            limit_start = cint(frappe.request.args["page"]) - 1
            if limit_start < 0:
                limit_start = 1
        if "order_by" in frappe.request.args:
            order_by = frappe.request.args["order_by"]
        else:
            order_by = order_by

        if "filters" in frappe.request.args:
            filters = frappe.request.args["filters"]
            if isinstance(filters, dict):
                filters = filters
            else:
                filters = frappe.parse_json(filters)
            if isinstance(filters, dict):
                filters = filters
            elif isinstance(filters, list):
                filters = filters
            else:
                filters = {}

        if force_user_filters:
            if isinstance(filters, dict):
                filters.update(user_filters)
            elif isinstance(filters, list):
                for k, v in user_filters.items():
                    val = [k,]
                    if isinstance(v, list):
                        val += v
                    else:
                        val += ["=", v]
                    filters.append(val)
        else:
            if not filters:
                filters = user_filters
            if user_filters:
                user_filters.update(filters)
                filters = user_filters

        if "or_filters" in frappe.request.args:
            or_filters = frappe.request.args["or_filters"]
            if isinstance(or_filters, list):
                or_filters = or_filters
            else:
                or_filters = frappe.parse_json(or_filters)

            if isinstance(or_filters, list):
                or_filters = or_filters
            else:
                or_filters = None
        if not force_fields:
            if "fields" in frappe.request.args:
                _fields = frappe.request.args["fields"]
                if isinstance(_fields, list):
                    _fields = _fields
                else:
                    _fields = frappe.parse_json(_fields)

                if isinstance(_fields, list):
                    fields = _fields
            if "*" in fields:
                fields = "*"
        limit_start = limit_start * limit_page_length
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
        # evaluate frappe.get_list
        data = frappe.call(frappe.client.get_list, doctype, **args)
        if translate_text and tr_field:
            lang=frappe.db.get_value("User", frappe.session.user, "language")
            for d in data:
                d.update({
                    f"{tr_field}": _(d[tr_field], lang=lang) if lang != "en" else d[tr_field]
                })
        load_extra_list_data(data, doctype)
        response_data = frappe._dict()
        response_data.update(
            {
                "data_list": data,
                "doctype": doctype,
                "page": limit_start + 1,
                "perPage": limit_page_length,
                "totalCount": count,
                "pageCount": len(data),
            }
        )
        return build_success_response(200, f"{doctype} fetched", response_data)
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
        return build_error_response(
            http_status_code, f"failed to read {doctype}", message
        )


def create_doc(doctype: str, default_data={}):
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
        doc.insert()
        delete_duplicated_or_after_error(uploaded_files)
        return build_success_response(201, f"{doctype} created", doc)
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
    last_check_in = frappe.get_all("Employee Checkin", filters={"employee": name}, fields=["log_type", "time"], order_by="time desc")
    if len(last_check_in):
        last_check_in = last_check_in[0]
    else:
        last_check_in = None
    extra_data.update({
        "checkin_status": last_check_in
    })
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
                                    date_of_issue, attachment, status, docstatus
                            FROM `tabEmployee Certification`
                            WHERE employee='{}'""".format(
                name
            ),
            as_dict=True,
        )
        achievements = frappe.db.sql(
            """
                            SELECT name, employee, employee_name, title, date, description,
                                    attachment, status, docstatus
                            FROM `tabEmployee Achievement`
                            WHERE employee='{}'""".format(
                name
            ),
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
                            WHERE docstatus=1 AND custodian='{}'""".format(
                name
            ),
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


def read_doc(
    doctype: str,
    name: str,
    origin_fields: list = [],
    force_fields=False,
    ignore_perms=False,
    load_extra_docs=True,
    load_checkin=False
):
    try:
        doc = frappe.get_doc(doctype, name)
        if not ignore_perms and not doc.has_permission("read"):
            raise frappe.PermissionError
        doc.apply_fieldlevel_read_permissions()
        extra_data = {}
        if load_extra_docs:
            extra_data = load_extra_data(doc.doctype, doc.name)
        if load_checkin:
            extra_data = load_extra_load_checkin_data(doc.doctype, doc.name)

        user_fields = origin_fields
        if not force_fields:
            if "fields" in frappe.request.args:
                _fields = frappe.request.args["fields"]
                if isinstance(_fields, list):
                    user_fields = _fields
                else:
                    user_fields = frappe.parse_json(_fields)

                if isinstance(_fields, list):
                    user_fields = _fields

            if "*" in user_fields:
                user_fields = []
        if doc:
            # getdoctype(doctype, True)
            get_docinfo(doc)
            doc = doc.as_dict()
        if len(user_fields) > 0:
            result = frappe._dict()
            for field in user_fields:
                if hasattr(doc, field):
                    result.update({field: getattr(doc, field)})
            doc = result
        translate_link_fields(doctype, doc)
        return build_success_response(200, f"{doctype} fetched", doc, extra_data)
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
        return build_error_response(
            http_status_code, f"failed to read {doctype}", message
        )


def update_doc(
    doctype: str, name: str, default_data={}, ignore_perms=False, keys_to_update=[]
):
    uploaded_files = []
    find_by = {"name": name}
    if default_data:
        find_by.update(default_data)
    doc = None
    try:
        data = get_request_form_data()
        doc = frappe.get_doc(doctype, find_by, for_update=True)
        if not isinstance(data, bytes):
            if "flags" in data:
                del data["flags"]
            data = format_data(data, doctype, keys_to_update=keys_to_update)
            doc.update(data)
        uploaded_files = handle_files(doc)
        for file in uploaded_files:
            fieldname = file.get("fieldname")
            doc.update(
                {
                    f"{fieldname}": file.get("file_url"),
                }
            )
        doc.update(default_data)
        doc.save(ignore_permissions=ignore_perms)
        delete_duplicated_or_after_error(uploaded_files)
        # check for child table doctype
        if doc.get("parenttype"):
            frappe.get_doc(doc.parenttype, doc.parent).save()
        return build_success_response(200, f"{doctype} updated", doc)
    except Exception as exc:
        return handle_exception_response(
            doc, doctype, exc, uploaded_files=uploaded_files, for_update=True
        )


def delete_doc(doctype: str, name: str):
    try:
        doc = frappe.delete_doc(doctype, name, ignore_missing=False)
        # frappe.response.http_status_code = 202
        return build_success_response(202, f"{doctype} deleted", doc)
    except Exception as exc:
        return handle_exception_response(
            None, doctype, exc, uploaded_files=[], for_delete=True
        )


def handle_call(method: str):
    import frappe.handler

    method = method.split("/")[0]
    frappe.form_dict.cmd = method
    return frappe.handler.handle()
