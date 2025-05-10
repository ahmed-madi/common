import frappe
def execute():
    for reason in ['Promotion', 'Contract Revision', 'Adjustment']:
        frappe.get_doc({
            "doctype": "Fixation Reason",
            "fixation_reason": reason,
        }).insert()
    frappe.db.commit()
