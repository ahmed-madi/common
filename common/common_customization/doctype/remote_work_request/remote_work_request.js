// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Remote Work Request", {
  from_date(frm) {
    frm.trigger("set_total_days");
  },
  to_date(frm) {
    frm.trigger("set_total_days");
  },
  employee(frm) {
    frm.trigger("validate_total_days");
  },
  set_total_days(frm) {
    if (frm.doc.from_date && frm.doc.to_date) {
      const from_date = new Date(frm.doc.from_date);
      const to_date = new Date(frm.doc.to_date);
      let diff = to_date - from_date;
      if (diff < 0) {
        frappe.show_alert(
          {
            message: __("To date cannot be before from date"),
            indicator: "red",
          },
          5
        );
        diff = 0;
      }
      const diffInDays = diff / (1000 * 60 * 60 * 24) + 1;
      if (diffInDays > 12) {
        frappe.show_alert(
          {
            message: __("Total request days cannot exceed 12 days"),
            indicator: "red",
          },
          5
        );
        diffInDays = 0;
      } else {
        frm.trigger("validate_total_days");
      }
      frm.set_value("total_days", diffInDays);
    } else {
      frm.set_value("total_days", 0);
    }
  },
  validate_total_days(frm) {
    if (
      frm.doc.from_date &&
      frm.doc.to_date &&
      frm.doc.employee &&
      frm.doc.total_days
    )
      frappe.call({
        doc: frm.doc,
        args: {
          // name, from_date, employee, total_days
          name: frm.doc.name,
          from_date: frm.doc.from_date,
          employee: frm.doc.employee,
          total_days: frm.doc.total_days,
          xclient: true,
        },
        method: "validate_total_requests",
        callback: function (r) {
          if (r && r.message) {
            frappe.show_alert({ message: r.message, indicator: "red" });
            // frm.set_value("total_hours", 0);
          }
        },
      });
  },
});
