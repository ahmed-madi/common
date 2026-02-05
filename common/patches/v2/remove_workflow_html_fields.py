import frappe


def execute():
    """
    Remove old workflow HTML custom fields (workflow_history_html and workflow_pending_actions_html)
    as we've migrated to timeline-based workflow actions.
    """
    # Get all custom fields with these fieldnames
    custom_fields_to_remove = frappe.get_all(
        "Custom Field",
        filters={
            "fieldname": [
                "in",
                ["workflow_history_html", "workflow_pending_actions_html"],
            ]
        },
        fields=["name", "dt", "fieldname"],
    )

    for cf in custom_fields_to_remove:
        try:
            frappe.delete_doc("Custom Field", cf.name, force=True)
            frappe.db.commit()
            print(f"Deleted Custom Field: {cf.fieldname} from {cf.dt}")
        except Exception as e:
            print(f"Error deleting Custom Field {cf.name}: {str(e)}")
            frappe.db.rollback()

    print(f"Removed {len(custom_fields_to_remove)} workflow HTML custom fields")
