import frappe

def get_request_form_data():
    if frappe.form_dict.data is None:
        data = frappe.safe_decode(frappe.request.get_data())
    else:
        data = frappe.form_dict.data
    try:
        return frappe.parse_json(data)
    except ValueError:
        return frappe.form_dict

def get_token_from_header():
    jwt_token = ""
    auth_header = frappe.request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        jwt_token = auth_header.split(" ")[1]
    return jwt_token
