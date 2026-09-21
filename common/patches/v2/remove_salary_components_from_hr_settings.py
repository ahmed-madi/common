import frappe

HR_SETTINGS = "HR Settings"
SALARY_COMPONENT = "Salary Component"


def execute():
    """Take the salary component configuration off HR Settings.

    Which component counts as basic, housing or transportation is configured
    in Company Policy, and read from there by the end of service award, the
    employee's salary figures and the salary identification letter. Anything
    on HR Settings saying the same thing is a second answer to one question,
    and the two can disagree.

    Fields are found by what they reference rather than by name, because a
    site may have named them anything. Leave and attendance settings reference
    leave and attendance doctypes, so they cannot be caught by this.
    """
    for field in get_salary_component_fields():
        remove_field(field)


def get_salary_component_fields():
    """Custom fields on HR Settings that configure salary components.

    Either a Link straight to Salary Component, or a table whose rows point at
    one - which is the shape a component-to-category mapping takes.
    """
    fields = []

    for field in frappe.get_all(
        "Custom Field",
        filters={"dt": HR_SETTINGS},
        fields=["name", "fieldname", "fieldtype", "options", "label"],
    ):
        if field.fieldtype == "Link" and field.options == SALARY_COMPONENT:
            fields.append(field)
        elif field.fieldtype == "Table" and child_table_holds_components(field.options):
            fields.append(field)

    return fields


def child_table_holds_components(child_doctype):
    """True when a child doctype's rows name a salary component."""
    if not child_doctype or not frappe.db.exists("DocType", child_doctype):
        return False

    meta = frappe.get_meta(child_doctype)

    return any(
        df.fieldtype == "Link" and df.options == SALARY_COMPONENT for df in meta.fields
    )


def remove_field(field):
    """Drop the field, its stored value, and any property setter for it."""
    if field.fieldtype == "Table":
        clear_child_rows(field.options)
    else:
        clear_single_value(field.fieldname)

    for property_setter in frappe.get_all(
        "Property Setter",
        filters={"doc_type": HR_SETTINGS, "field_name": field.fieldname},
        pluck="name",
    ):
        frappe.delete_doc(
            "Property Setter", property_setter, force=1, ignore_permissions=True
        )

    frappe.delete_doc("Custom Field", field.name, force=1, ignore_permissions=True)

    frappe.logger().info(
        f"Removed salary component field {field.fieldname} ({field.label}) from {HR_SETTINGS}"
    )


def clear_child_rows(child_doctype):
    """Delete the table's rows, which the field is about to stop describing.

    Only the rows parented to HR Settings - the same child doctype may well be
    in use somewhere that is keeping it.
    """
    if not child_doctype or not frappe.db.table_exists(child_doctype):
        return

    frappe.db.delete(child_doctype, {"parent": HR_SETTINGS, "parenttype": HR_SETTINGS})


def clear_single_value(fieldname):
    """HR Settings is a Single, so its values live in tabSingles."""
    frappe.db.delete("Singles", {"doctype": HR_SETTINGS, "field": fieldname})
