import json
import frappe
from frappe.utils.data import sbool

from common.api.utils import get_request_form_data
from common.api.utils.response import build_error_response, build_success_response

def document_list(doctype: str, fields: list | str):
    filters=None
    or_filters=None
    group_by=None
    order_by=None
    limit_start=0
    limit_page_length=20
    parent=None
    try:
        if frappe.form_dict.get("fields"):
            frappe.form_dict["fields"] = json.loads(frappe.form_dict["fields"])

        # set limit of records for frappe.get_list
        frappe.form_dict.setdefault(
            "limit_page_length",
            frappe.form_dict.limit or frappe.form_dict.limit_page_length or 20,
        )

        frappe.form_dict.setdefault(
            "limit_start",
            frappe.form_dict.page or frappe.form_dict.limit_start or 0,
        )

        # convert strings to native types - only as_dict and debug accept bool
        for param in ["as_dict", "debug"]:
            param_val = frappe.form_dict.get(param)
            if param_val is not None:
                frappe.form_dict[param] = sbool(param_val)

        filters = frappe.form_dict.get("filters")
        or_filters = frappe.form_dict.get("or_filters")
        group_by = frappe.form_dict.get("group_by")
        order_by = frappe.form_dict.get("order_by")
        limit_start = frappe.form_dict.get("limit_start")
        limit_page_length = frappe.form_dict.get("limit_page_length")
        parent = frappe.form_dict.get("parent")

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
        # evaluate frappe.get_list
        data = frappe.call(frappe.client.get_list, doctype, **args)
        return build_success_response(202, f"{doctype} fetched", data)
    except frappe.DoesNotExistError as exc:
        return build_error_response(404, f"failed to read {doctype}", exc)
    except Exception as exc:
        return build_error_response(500, f"failed to read {doctype}", exc)

def create_doc(doctype: str):
    try:
        data = get_request_form_data()
        data.pop("doctype", None)
        doc = frappe.new_doc(doctype, **data).insert()
        return build_success_response(200, f"{doctype} created", doc)
    except Exception as exc:
        return build_error_response(500, f"failed to create {doctype}", exc)

def read_doc(doctype: str, name: str):
    try:
        doc = frappe.get_doc(doctype, name)
        if not doc.has_permission("read"):
            raise frappe.PermissionError
        doc.apply_fieldlevel_read_permissions()
        # frappe.response.http_status_code = 202
        return build_success_response(202, f"{doctype} fetched", doc)
    except Exception as exc:
        return build_error_response(500, f"failed to read {doctype}", exc)

def update_doc(doctype: str, name: str):
    try:
        data = get_request_form_data()
        doc = frappe.get_doc(doctype, name, for_update=True)
        if "flags" in data:
            del data["flags"]
        doc.update(data)
        doc.save()
        # check for child table doctype
        if doc.get("parenttype"):
            frappe.get_doc(doc.parenttype, doc.parent).save()
        return build_success_response(200, f"{doctype} updated", doc)
    except Exception as exc:
        return build_error_response(500, f"failed to update {doctype}", exc)

def delete_doc(doctype: str, name: str):
    try:
        doc = frappe.delete_doc(doctype, name, ignore_missing=False)
        # frappe.response.http_status_code = 202
        return build_success_response(202, f"{doctype} deleted", doc)
    except Exception as exc:
        return build_error_response(500, f"failed to delete {doctype}", exc)

def handle_call(method: str):
    import frappe.handler
    method = method.split("/")[0]
    frappe.form_dict.cmd = method
    return frappe.handler.handle()
    
