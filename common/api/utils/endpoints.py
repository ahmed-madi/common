import frappe
from frappe.utils import cint

from common.api.utils import get_request_form_data, upload_file, delete_duplicated_or_after_error
from common.api.utils.response import build_error_response, build_success_response

# All errors when create doc
from hrms.hr.doctype.leave_application.leave_application import OverlapError

def document_list(doctype: str, fields: list | str):
    filters=None
    or_filters=None
    group_by=None
    order_by=None
    limit_start=0
    limit_page_length=20
    parent=None
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
        if "order_by"  in frappe.request.args:
            order_by = frappe.request.args["order_by"]

        if "filters"  in frappe.request.args:
            filters = frappe.request.args["filters"]
            if isinstance(filters, dict):
                filters = filters
            else:
                filters = frappe.parse_json(filters)
            
            if isinstance(filters, dict):
                filters = filters
            else:
                filters = None

        if "or_filters"  in frappe.request.args:
            or_filters = frappe.request.args["or_filters"]
            if isinstance(or_filters, list):
                or_filters = or_filters
            else:
                or_filters = frappe.parse_json(or_filters)
            
            if isinstance(or_filters, list):
                or_filters = or_filters
            else:
                or_filters = None
        if "fields"  in frappe.request.args:
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
        response_data = frappe._dict()
        response_data.update({
            "data_list": data,
            "page": limit_start+1,
            "perPage": limit_page_length,
            "totalCount": count,
            "pageCount": len(data),
        })
        return build_success_response(200, f"{doctype} fetched", response_data)
    except Exception as exc:
        http_status_code = 500
        message = exc
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 0:
                message = args[0].split(":")[0]
        return build_error_response(http_status_code, f"failed to read {doctype}", message)

def create_doc(doctype: str):
    uploaded_files = []
    doc = None
    try:
        data = get_request_form_data()
        data.pop("doctype", None)
        doc = frappe.new_doc(doctype, **data)
        uploaded_files = handle_files(doc)
        for file in uploaded_files:
            fieldname = file.get("fieldname")
            doc.update({
                f"{fieldname}": file.get("file_url"),
            })
        doc.insert()
        delete_duplicated_or_after_error(uploaded_files)
        return build_success_response(201, f"{doctype} created", doc)
    except frappe.MandatoryError as exc:
        http_status_code = 500
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        errors = doc._get_missing_mandatory_fields()
        missing_fields = [er[0] for er in errors]
        return build_error_response(http_status_code, f"failed to create {doctype}", "Required values are missing", missing_fields)
    except Exception as exc:
        http_status_code = 500
        message = exc
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 0:
                message = args[0].split(":")[0]
                if message == "Cannot link cancelled document":
                    message = args[0]
        delete_duplicated_or_after_error(uploaded_files)
        return build_error_response(http_status_code, f"failed to create {doctype}", message)

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

def read_doc(doctype: str, name: str, origin_fields:list=[]):
    try:
        doc = frappe.get_doc(doctype, name)
        if not doc.has_permission("read"):
            raise frappe.PermissionError
        doc.apply_fieldlevel_read_permissions()

        user_fields = origin_fields
        if "fields"  in frappe.request.args:
            _fields = frappe.request.args["fields"]
            if isinstance(_fields, list):
                user_fields = _fields
            else:
                user_fields = frappe.parse_json(_fields)
            
            if isinstance(_fields, list):
                user_fields = _fields
 
        if "*" in user_fields:
            user_fields = []

        if len(user_fields) > 0:
            doc = doc.as_dict()
            result = frappe._dict()
            for field in user_fields:
                if hasattr(doc, field):
                    result.update({
                        field: getattr(doc, field)
                    })
            doc = result

        return build_success_response(200, f"{doctype} fetched", doc)
    except Exception as exc:
        http_status_code = 500
        message = exc
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 0:
                message = args[0].split(":")[0]
        return build_error_response(http_status_code, f"failed to read {doctype}", message)

def update_doc(doctype: str, name: str):
    uploaded_files = []
    try:
        data = get_request_form_data()
        doc = frappe.get_doc(doctype, name, for_update=True)
        if "flags" in data:
            del data["flags"]
        doc.update(data)
        uploaded_files = handle_files(doc)
        for file in uploaded_files:
            fieldname = file.get("fieldname")
            doc.update({
                f"{fieldname}": file.get("file_url"),
            })
        doc.save()
        delete_duplicated_or_after_error(uploaded_files)
        # check for child table doctype
        if doc.get("parenttype"):
            frappe.get_doc(doc.parenttype, doc.parent).save()
        return build_success_response(200, f"{doctype} updated", doc)
    except Exception as exc:
        delete_duplicated_or_after_error(uploaded_files)
        http_status_code = 500
        message = exc
        print(exc)
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        if hasattr(exc, "args"):
            args = exc.args
            if len(args) > 0:
                message = args[0].split(":")[0]
        return build_error_response(http_status_code, f"failed to update {doctype}", message)

def delete_doc(doctype: str, name: str):
    try:
        doc = frappe.delete_doc(doctype, name, ignore_missing=False)
        # frappe.response.http_status_code = 202
        return build_success_response(202, f"{doctype} deleted", doc)
    except Exception as exc:
        http_status_code = 500
        message = f"{exc}"
        if hasattr(exc, "http_status_code"):
            http_status_code = exc.http_status_code
        return build_error_response(http_status_code, f"failed to delete {doctype}", message)

def handle_call(method: str):
    import frappe.handler
    method = method.split("/")[0]
    frappe.form_dict.cmd = method
    return frappe.handler.handle()
    
