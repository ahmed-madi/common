// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Change IBAN Request", {
    refresh(frm) {
        frm.set_query("employee", function (doc) {
            return {
                filters: {
                    status: "Active",
                },
            };
        });
    },
    employee(frm){
        frm.set_value('bank_name', '')
        frm.set_value('bank_ac_no', '')
        frm.set_value('iban', '')
        frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Employee",
				filters: { name: frm.doc.employee },
				fieldname: [
					"bank_name",
					"bank_ac_no",
					"iban",
				],
			},
			callback: (r) => {
				if (r.message) {
                    Object.keys(r.message).forEach(field => {
                        frm.set_value(field, r.message[field])
                    })
                    
				}
			},
		});
    },
});
