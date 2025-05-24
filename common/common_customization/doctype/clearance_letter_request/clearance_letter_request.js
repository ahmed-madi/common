// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Clearance Letter Request", {
	setup(frm) {
        frm.set_query("employee", function (doc) {
            return {
                filters: {
                    status: "Active",
                },
            };
        });
    },
});
