// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cancel Leave Application", {
    refresh(frm) {
        frm.set_query("employee", (doc) => {
            return {
                filters: {
                    status: "Active"
                }
            }
        });

        frm.set_query("leave_application", (doc) => {
            return {
                filters: {
                    status: "Approved",
                    docstatus: 1,
                    employee: doc.employee,
                }
            }
        });
    },
    employee(frm) {
        frm.set_value("leave_application", null);
        frm.refresh_field("leave_application");
    }
});
