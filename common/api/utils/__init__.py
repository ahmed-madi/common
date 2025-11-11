import frappe
from frappe.utils import cint, flt


def format_data(data, doctype, keys_to_update=[]):
    if not isinstance(data, dict):
        return data
    valid_data = {}
    meta = frappe.get_meta(doctype)
    has_keys = len(keys_to_update) > 0
    for k, v in data.items():
        if has_keys and k not in keys_to_update:
            continue
        field = meta.get_field(k)
        if not field:
            continue
        if field.fieldtype in ["Currency", "Float", "Percent"]:
            v = flt(v)
        elif field.fieldtype in ["Int", "Check"]:
            v = cint(v)
        valid_data.update(
            {
                f"{k}": v,
            }
        )
    return valid_data


def get_request_form_data():
    if frappe.form_dict.data is None:
        data = frappe.safe_decode(frappe.request.get_data())
    else:
        data = frappe.form_dict.data
    try:
        if isinstance(data, bytes):
            values = frappe.request.values.to_dict()
            if values:
                return values
        return frappe.parse_json(data)
    except ValueError:
        values = frappe.request.values.to_dict()
        if values:
            return values
        return frappe.form_dict


def get_token_from_header():
    jwt_token = ""
    auth_header = frappe.request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        jwt_token = auth_header.split(" ")[1]
    return jwt_token


def upload_file(fieldname):
    if fieldname not in frappe.request.files:
        return None
    file = frappe.request.files[fieldname]
    if not file or file is None:
        return None
    file_url = None
    if library_file := frappe.form_dict.get("library_file_name"):
        frappe.has_permission("File", doc=library_file, throw=True)
        doc = frappe.get_value(
            "File",
            frappe.form_dict.library_file_name,
            ["is_private", "file_url", "file_name"],
            as_dict=True,
        )
        file_url = doc.file_url
        filename = doc.file_name

    content = file.stream.read()
    filename = file.filename

    file_doc = frappe.get_doc(
        {
            "doctype": "File",
            # "attached_to_doctype": doctype,
            # "attached_to_name": docname,
            "attached_to_field": fieldname,
            "file_name": filename,
            "file_url": file_url,
            "content": content,
        }
    ).save()
    file_doc = frappe.get_doc("File", file_doc.name)
    file_doc.save()
    return {
        "name": file_doc.name,
        "file_url": file_doc.file_url,
        "fieldname": fieldname,
    }


def delete_duplicated_or_after_error(uploaded_files):
    for file in uploaded_files:
        if not file.get("name"):
            continue
        frappe.delete_doc_if_exists("File", file.get("name"))


def handle_password_test_fail(feedback: dict):
    # Backward compatibility
    if "feedback" in feedback:
        feedback = feedback["feedback"]

    suggestions = feedback.get("suggestions", [])
    warning = feedback.get("warning", "")
    if warning:
        return " ".join([warning, *suggestions])
    return " ".join(suggestions)
