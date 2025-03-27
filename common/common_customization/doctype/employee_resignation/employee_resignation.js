// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Resignation", {
  refresh: function (frm) {
    if (frm.is_new()) frm.trigger("set_reasons_for_resignation_options");
  },
  custom_employment_type(frm) {
    frm.trigger("set_reasons_for_resignation_options");
    frm.trigger("set_end_of_service_date");
  },
  set_reasons_for_resignation_options(frm) {
    let options = "\nNot wanting to renew the contract\nSubmit resignation";
    frm.set_df_property("reasons_for_resignation", "options", options);
    if (!frm.doc.employee || !frm.doc.custom_employment_type) {
      return;
    }
    frappe.dom.freeze();
    frappe.db
      .get_single_value(
        "HR Settings",
        "custom_employment_type_for_trial_period"
      )
      .then((val) => {
        if (frm.doc.custom_employment_type == val) {
          options += "\nEnding the trial period";
        }
        frm.set_df_property("reasons_for_resignation", "options", options);
        frappe.dom.unfreeze();
      })
      .catch((err) => {
        frappe.dom.unfreeze();
      });
  },
  reasons_for_resignation(frm) {
    frm.trigger("set_end_of_service_date");
  },
  custom_employment_type_for_trial_period() {
    frm.trigger("set_end_of_service_date");
  },
  set_end_of_service_date(frm) {
    if (frm.doc.reasons_for_resignation !== "Ending the trial period") {
      frm.set_value(
        "end_service_date",
        frappe.datetime.add_days(frm.doc.date_of_joining, 60)
      );
    } else {
      frm.set_value("end_service_date", frm.doc.date);
    }
  },
});
