import frappe
from frappe.model import table_fields

DOCTYPE = "Company Policy"

# The name the Single went by, which is what its child rows are parented to.
SINGLE_NAME = "Company Policy"


def execute():
    """Give every company its own copy of the one policy the site had.

    Company Policy used to be a Single: one set of HR rules for the whole site.
    A group running companies in more than one country needs one per company,
    so the doctype now has a record each.

    Nobody re-enters what a site already configured. Every company starts from
    the settings that were in force for all of them, and diverges from there
    only where it needs to.
    """
    if not frappe.db.table_exists(DOCTYPE):
        return

    values = get_single_values()
    child_rows = get_single_child_rows()

    companies = frappe.get_all("Company", pluck="name")
    if not companies:
        return

    created = []
    for company in companies:
        if frappe.db.exists(DOCTYPE, company):
            continue

        create_policy(company, values, child_rows)
        created.append(company)

    if created:
        clear_single_data()
        frappe.db.commit()
        frappe.logger().info(
            f"Company Policy is now per company. Seeded: {', '.join(created)}"
        )


def get_single_values():
    """The Single's stored settings, as a plain dict of field to value."""
    rows = frappe.get_all(
        "Singles",
        filters={"doctype": DOCTYPE},
        fields=["field", "value"],
    )

    return {row.field: row.value for row in rows}


def get_single_child_rows():
    """The Single's table rows, keyed by the table they belong to.

    Read once and copied to every company, so each one starts with the same
    salary component categories and whitelist roles the site already had.
    """
    meta = frappe.get_meta(DOCTYPE)
    rows = {}

    for df in meta.get_table_fields():
        if not frappe.db.table_exists(df.options):
            continue

        rows[df.fieldname] = frappe.get_all(
            df.options,
            filters={"parent": SINGLE_NAME, "parenttype": DOCTYPE},
            fields=["*"],
            order_by="idx asc",
        )

    return rows


def create_policy(company, values, child_rows):
    """Write the settings out as one company's policy.

    Inserted without validation: these values were already accepted once, and
    a rule added since must not stop a site from keeping the settings it has.
    """
    policy = frappe.new_doc(DOCTYPE)
    meta = frappe.get_meta(DOCTYPE)

    for fieldname, value in values.items():
        df = meta.get_field(fieldname)
        if df and df.fieldtype not in table_fields:
            policy.set(fieldname, value)

    for fieldname, rows in child_rows.items():
        for row in rows:
            child = {
                key: value
                for key, value in row.items()
                # The copy is a new row of its own, so it keeps none of the
                # original's identity or parentage.
                if key
                not in (
                    "name",
                    "parent",
                    "parenttype",
                    "parentfield",
                    "creation",
                    "modified",
                    "owner",
                    "modified_by",
                    "idx",
                    "docstatus",
                )
            }
            policy.append(fieldname, child)

    policy.company = company
    policy.name = company
    policy.flags.ignore_validate = True
    policy.flags.ignore_mandatory = True
    policy.flags.ignore_links = True
    policy.insert(ignore_permissions=True)


def clear_single_data():
    """Drop what the Single left behind, once every company has its own copy.

    The Singles rows would otherwise shadow the records, and the orphaned child
    rows still point at a parent that no longer exists.
    """
    meta = frappe.get_meta(DOCTYPE)

    for df in meta.get_table_fields():
        if frappe.db.table_exists(df.options):
            frappe.db.delete(df.options, {"parent": SINGLE_NAME, "parenttype": DOCTYPE})

    frappe.db.delete("Singles", {"doctype": DOCTYPE})
