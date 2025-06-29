// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salary Fixation", {
	setup(frm) {
        frm.set_query("employee", function(doc){
            return {
                filters: {
                    // salary_mode: "Bank",
                    // iban: ["is", "set"],
                    status: 'Active'
                }
            }
        })
	},
});
