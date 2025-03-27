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
  onload: function (frm) {
    frm.fields_dict["overtime_request"].onchange = function () {
      var overtimeRequest = frm.doc.overtime_request;

      // Fetch time_logs from the selected Overtime Request and set it to time_logs field in Overtime Pay Request
      frappe.call({
        method: "fetch_time_logs",
        doc: frm.doc,
        args: {
          overtime_request: overtimeRequest,
        },
        callback: function (response) {
          if (response.message) {
            console.log(response.message);
            frm.set_value("time_logs", response.message);
          }
        },
      });
    };
  },
});
