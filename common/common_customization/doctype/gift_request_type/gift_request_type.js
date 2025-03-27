// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gift Request Type", {
  refresh: function (frm) {
    frm.set_query("salary_component", function () {
      return {
        filters: {
          company: frappe.defaults.get_default("company"),
        },
      };
    });
  },

  total_months(frm) {
    if (cint(frm.doc.total_months) <= 0) {
      frappe.show_alert(
        {
          message: __("Total months must be at least 1 month"),
          indicator: "red",
        },
        5
      );
      frm.set_value("total_months", 1);
    }
    frm.set_value("total_cost", cint(frm.doc.total_months) * frm.doc.gift_cost);
  },
  allowed_requests(frm) {
    frm.set_value("allowed_requests", cint(frm.doc.allowed_requests));
  },

  gift_cost(frm) {
    frm.set_value("total_cost", cint(frm.doc.total_months) * frm.doc.gift_cost);
  },
});
