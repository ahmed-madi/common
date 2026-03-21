import frappe
from frappe.utils import cint, flt
from bs4 import BeautifulSoup


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


def upload_file(fieldname, doctype=None, docname=None):
    if fieldname not in frappe.request.files:
        return None
    file = frappe.request.files[fieldname]
    if not file or file is None:
        return None

    # Default to private (1) for HR application unless specified otherwise
    is_private = cint(frappe.form_dict.get("is_private", 1))

    file_url = None
    if library_file := frappe.form_dict.get("library_file_name"):
        frappe.has_permission("File", doc=library_file, throw=True)
        doc = frappe.db.get_value(
            "File",
            library_file,
            ["is_private", "file_url", "file_name"],
            as_dict=True,
        )
        file_url = doc.file_url
        filename = doc.file_name
        # If from library, respect the library file's private status unless explicitly overridden
        if "is_private" not in frappe.form_dict:
            is_private = doc.is_private
    else:
        filename = file.filename

    content = file.stream.read()

    doc_dict = {
        "doctype": "File",
        "attached_to_field": fieldname,
        "file_name": filename,
        "file_url": file_url,
        "content": content,
        "is_private": is_private,
    }
    if doctype and docname:
        doc_dict.update(
            {
                "attached_to_doctype": doctype,
                "attached_to_name": docname,
            }
        )

    file_doc = frappe.get_doc(doc_dict).save(ignore_permissions=True)
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


def sanitize_html(html_content):
    if not html_content:
        return None
    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(["script", "iframe", "form", "frame", "object", "embed", "style"]):
        tag.decompose()
    for tag in soup.find_all(True):
        if tag.name == "a":
            span_tag = soup.new_tag("span")
            span_tag.string = tag.get_text()
            tag.replace_with(span_tag)
            continue

        tag.attrs.clear()

    return str(soup)


def update_files_to_doc(doctype: str, doc: "frappe.model.document.Document", uploaded_files: list):
    """
    Updates file attachments for a document.
    Handles:
    1. Setting field values in the doc object (mandatory for new docs before save).
    2. Linking File records to the document (after save).
    3. Deleting old File records for the same field to avoid duplicates/sidebar clutter.
    """
    for file in uploaded_files:
        fieldname = file.get("fieldname")
        file_url = file.get("file_url")
        file_name = file.get("name")

        if not fieldname or not file_url:
            continue

        # 1. Update the document object/database field
        if hasattr(doc, "set"):
            doc.set(fieldname, file_url)

        # 2. Link the File record to the document if it has a name
        if doc.name and not doc.name.startswith("New "):
            frappe.db.set_value(
                "File",
                file_name,
                {
                    "attached_to_doctype": doctype,
                    "attached_to_name": doc.name,
                    "attached_to_field": fieldname,
                },
                update_modified=False,
            )

            # 3. Handle Duplicate Records (Delete old attachments for this field)
            # Find files attached to this doctype, name, and field, but NOT the one we just uploaded
            old_files = frappe.get_all(
                "File",
                filters={
                    "attached_to_doctype": doctype,
                    "attached_to_name": doc.name,
                    "attached_to_field": fieldname,
                    "name": ["!=", file_name],
                },
                pluck="name",
            )

            for old_file in old_files:
                frappe.delete_doc("File", old_file, ignore_missing=True)

            # 4. Final sync to DB if doc is already saved (just in case set_value is needed)
            frappe.db.set_value(
                doctype,
                doc.name,
                fieldname,
                file_url,
                update_modified=False,
            )
