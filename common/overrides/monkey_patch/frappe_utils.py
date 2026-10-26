import frappe


def get_link_to_form(doctype: str, name: str | None = None, label: str | None = None) -> str:
    if not label:
        label = name or frappe._(doctype)
    if frappe.flags.get("api_call", False):
        return label
    return (
        f"""<a href="{frappe.utils.data.get_url_to_form(doctype, name)}">{label}</a>"""
    )


def bold(text: str | int | float) -> str:
    if frappe.flags.get("api_call", False):
        return text
    return f"<strong>{text}</strong>"


def patch_frappe_utils():
    frappe.utils.data.get_link_to_form = get_link_to_form
    frappe.utils.get_link_to_form = get_link_to_form
    # v16 defines bold in frappe.utils.data and re-exports it from frappe
    frappe.utils.data.bold = bold
    frappe.utils.bold = bold
    frappe.bold = bold
