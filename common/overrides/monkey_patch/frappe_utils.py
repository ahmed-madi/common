import frappe


def get_link_to_form(doctype: str, name: str, label: str | None = None) -> str:
    if not label:
        label = name
    if frappe.flags.get("api_call", False):
        return label
    return (
        f"""<a href="{frappe.utils.data.get_url_to_form(doctype, name)}">{label}</a>"""
    )


def bold(text):
    if frappe.flags.get("api_call", False):
        return text
    return f"<strong>{text}</strong>"


def patch_frappe_utils():
    frappe.utils.data.get_link_to_form = get_link_to_form
    frappe.utils.get_link_to_form = get_link_to_form
    frappe.bold = bold
