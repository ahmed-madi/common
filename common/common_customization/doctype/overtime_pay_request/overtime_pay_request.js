// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Overtime Pay Request", {
  refresh: function (frm) {
    frm.fields_dict["overtime_request"].get_query = function (doc, cdt, cdn) {
      // Get the current document's docstatus
      return {
        filters: {
          // Add any other filters you need
          docstatus: 1,
          processed: 0,
        },
      };
    };
  },
});
