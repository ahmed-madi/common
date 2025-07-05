// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Achievement", {
    refresh(frm) {
        frm.set_query("employee", (doc) => {
            return {
                filters: {
                    status: "Active",
                },
            };
        });
    },
});
