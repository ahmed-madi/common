// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Work Outside Office Permission", {
  from_date(frm) {
    frm.trigger("set_total_days");
  },
  to_date(frm) {
    frm.trigger("set_total_days");
  },
  start_time(frm) {
    frm.trigger("set_total_hours");
  },
  end_time(frm) {
    frm.trigger("set_total_hours");
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
      const diffInDays = diff / (1000 * 60 * 60 * 24);
      frm.set_value("total_days", diffInDays);
    } else {
      frm.set_value("total_days", 0);
    }
  },
  set_total_hours(frm) {
    if (frm.doc.start_time && frm.doc.end_time) {
      const start_time = new Date("2000-01-01 " + frm.doc.start_time);
      const end_time = new Date("2000-01-01 " + frm.doc.end_time);

      let diff = end_time - start_time;
      if (diff < 0) {
        frappe.show_alert(
          {
            message: __("End time cannot be before start time"),
            indicator: "red",
          },
          5
        );
        diff = 0;
      }
      const diffInHours = diff / (1000 * 60 * 60);
      frm.set_value("total_hours", diffInHours.toFixed(6));
    } else {
      frm.set_value("total_hours", 0);
    }
  },
});
