// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Overtime Request", {
  refresh: function (frm) {
    frm.fields_dict["time_logs"].grid.get_field("project").get_query =
      function (doc, cdt, cdn) {
        var child = locals[cdt][cdn];

        // Set a custom filter for the 'project' field based on some condition
        // In this example, it filters tasks based on the project associated with the task
        return {
          filters: {
            project: child.project,
          },
        };
      };
  },
  onload: function (frm) {
    calculateTotalHours(frm);
  },

  // Trigger the calculation when the child table is updated
  time_logs_add: function (frm, cdt, cdn) {
    calculateTotalHours(frm);
  },

  // Trigger the calculation when the child table is deleted
  time_logs_remove: function (frm, cdt, cdn) {
    calculateTotalHours(frm);
  },
});
frappe.ui.form.on("Overtime Timesheet Detail", {
  hours: function (frm) {
    calculateTotalHours(frm);
  },
});

function calculateTotalHours(frm) {
  var totalHours = 0;
  console.log("HIT");
  // Iterate through the time_logs in the child table
  var i = 0;
  frm.doc.time_logs.forEach(function (entry) {
    // Calculate the time difference in hours
    var timeDiffHours = entry.hours;

    // Set the calculated hours to the 'hours' field

    // Accumulate the total hours
    totalHours += timeDiffHours || 0;
  });

  // Set the calculated total back to the main document
  console.log("HIT2");
  console.log(totalHours);

  frappe.model.set_value(frm.doctype, frm.docname, "total_hours", totalHours);
}
