// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Permission", {
  start_time(frm) {
    frm.trigger("set_total_hours");
  },
  end_time(frm) {
    frm.trigger("set_total_hours");
  },
  employee(frm) {
    frm.trigger("validate_total_hours_in_month");
  },
  day(frm) {
    frm.trigger("validate_total_hours_in_month");
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
      let diffInHours = diff / (1000 * 60 * 60);
      if (diffInHours > 4) {
        frappe.show_alert(
          {
            message: __("Total hours cannot be greater than 4"),
            indicator: "red",
          },
          5
        );
        diffInHours = 0;
      } else {
        frm.trigger("validate_total_hours_in_month");
      }
      frm.set_value("total_hours", diffInHours.toFixed(2));
    } else {
      frm.set_value("total_hours", 0);
    }
  },
  validate_total_hours_in_month(frm) {
    if (
      frm.doc.day &&
      frm.doc.employee &&
      frm.doc.end_time &&
      frm.doc.end_time &&
      frm.doc.total_hours
    )
      frappe.call({
        doc: frm.doc,
        args: {
          employee: frm.doc.employee,
          day: frm.doc.day,
          name: frm.doc.name,
          total_hours: frm.doc.total_hours,
          xclient: true,
        },
        method: "check_total_hours_in_month",
        callback: function (r) {
          if (r && r.message) {
            frappe.show_alert({ message: r.message, indicator: "red" });
            // frm.set_value("total_hours", 0);
          }
        },
      });
  },
});
