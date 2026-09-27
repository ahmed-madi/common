// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

cur_frm.add_fetch("employee", "date_of_joining", "work_start_date");

const RECALCULATE_METHOD =
  "common.common_customization.doctype.end_of_service_award.end_of_service_award.recalculate";

const CHECK_FIELDS = ["exclude_award_from_total"];
const TEXT_FIELDS = [
  "employee_name",
  "company",
  "type_of_contract",
  "department",
  "reason",
  "salary_structure",
];

function value_changed(fieldname, current, incoming) {
  if (TEXT_FIELDS.includes(fieldname)) {
    return (current || "") !== (incoming || "");
  }
  if (CHECK_FIELDS.includes(fieldname)) {
    return cint(current) !== cint(incoming);
  }
  return flt(current, 2) !== flt(incoming, 2);
}

// Writes what the server worked out onto the form. Only the values that
// actually changed are set, and the field handlers are told to stand down
// while they are, so setting a field never starts another recalculation.
async function apply_calculated_values(frm, values) {
  const changed = {};
  for (const [fieldname, value] of Object.entries(values || {})) {
    if (value_changed(fieldname, frm.doc[fieldname], value)) {
      changed[fieldname] = value;
    }
  }
  if (!Object.keys(changed).length) {
    return;
  }

  frm.__eosa_applying = true;
  try {
    await frm.set_value(changed);
  } finally {
    frm.__eosa_applying = false;
  }
}

// The one recalculation, done on the server by the same chain validate() runs,
// so the form and the saved doc can never disagree - the award formula is
// Python and could not be mirrored here anyway.
//
// Only one request is ever in flight. A change made while one is running marks
// the form for another pass, run with the latest values once it returns, so a
// slow response can never overwrite a newer one.
//
// `refetch` is set when the employee or a service date changed: the days
// number and the leave balance are then refilled rather than kept as entered.
function recalculate(frm, { refetch = false } = {}) {
  if (frm.__eosa_applying || frm.doc.docstatus !== 0) {
    return Promise.resolve();
  }

  frm.__eosa_refetch = frm.__eosa_refetch || refetch;
  if (frm.__eosa_running) {
    frm.__eosa_pending = true;
    return frm.__eosa_running;
  }

  frm.__eosa_running = (async () => {
    do {
      frm.__eosa_pending = false;
      const refetch_now = frm.__eosa_refetch;
      frm.__eosa_refetch = false;

      const { message } = await frappe.call({
        method: RECALCULATE_METHOD,
        args: { doc: frm.doc, refetch: refetch_now ? 1 : 0 },
      });
      await apply_calculated_values(frm, message);
    } while (frm.__eosa_pending);
  })().finally(() => {
    frm.__eosa_running = null;
    frm.__eosa_pending = false;
  });

  return frm.__eosa_running;
}

const recalculate_on_change = (frm) => recalculate(frm);
const recalculate_with_refetch = (frm) => recalculate(frm, { refetch: true });

frappe.ui.form.on("End of Service Award", {
  onload: function (frm) {
    // Only reasons that apply to the employee's company. A reason with no
    // company is a shared rule and is offered to all of them.
    frm.set_query("reason", function (doc) {
      return {
        query:
          "common.common_customization.doctype.end_of_service_award_reason.end_of_service_award_reason.get_reasons_for_company",
        filters: {
          company: doc.company,
        },
      };
    });

    frm.set_query("group_deductions_in", function (doc) {
      return {
        filters: {
          disabled: 0,
          type: "Deduction",
        },
      };
    });

    frm.set_query("group_earnings_in", function (doc) {
      return {
        filters: {
          disabled: 0,
          type: "Earning",
        },
      };
    });
  },
  refresh(frm) {
    $('div[data-fieldname="html_1"]').attr(
      "style",
      "visibility: hidden !important;"
    );
    $('div[data-fieldname="html_2"]').attr(
      "style",
      "visibility: hidden !important;"
    );

    if (frm.doc.docstatus === 1) {
      frappe.call({
        method:
          "common.common_customization.doctype.end_of_service_award.end_of_service_award.end_of_service_has_jv_entries",
        args: {
          name: frm.doc.name,
        },
        callback: function (r) {
          if (r.message && !r.message.submitted) {
            frm
              .add_custom_button(__("Make Journal Entry"), function () {
                return frappe.call({
                  doc: frm.doc,
                  method: "make_journal_entry",
                  callback: function () {
                    frappe.set_route("List", "Journal Entry", {
                      "Journal Entry Account.reference_name": frm.doc.name,
                      voucher_type: "Journal Entry",
                    });
                  },
                  freeze: true,
                  freeze_message: __("Creating Payment Entries......"),
                });
              })
              .addClass("btn-primary");
          }
        },
      });
      frappe.call({
        method:
          "common.common_customization.doctype.end_of_service_award.end_of_service_award.end_of_service_has_bank_jv_entries",
        args: {
          name: frm.doc.name,
        },
        callback: function (r) {
          if (r.message && r.message.submitted_jv == 0) {
            return;
          }
          if (r.message && !r.message.submitted) {
            frm
              .add_custom_button(__("Make Bank Entry"), function () {
                return frappe.call({
                  doc: frm.doc,
                  method: "make_bank_entry",
                  callback: function () {
                    frappe.set_route("List", "Journal Entry", {
                      "Journal Entry Account.reference_name": frm.doc.name,
                      voucher_type: "Bank Entry",
                    });
                  },
                  freeze: true,
                  freeze_message: __("Creating Payment Entries......"),
                });
              })
              .addClass("btn-primary");
          }
        },
      });
    }
  },

  // A save must not race a recalculation still in flight. The server works
  // everything out again on save regardless, from the reason and the
  // employee's current record.
  validate: function (frm) {
    return frm.__eosa_running;
  },

  // A new employee, or new service dates, change everything from the salary
  // and the service duration down - and refill the days number and the leave
  // balance, which otherwise keep a manual override.
  employee: recalculate_with_refetch,
  end_date: recalculate_with_refetch,
  work_start_date: recalculate_with_refetch,

  days_number: recalculate_on_change,
  salary_is_already_taken: recalculate_on_change,
  leave_number: recalculate_on_change,
  ticket_number: recalculate_on_change,
  ticket_cost: recalculate_on_change,
  reason: recalculate_on_change,

  notice_month: function (frm) {
    frm.set_df_property("notice_month_start", "reqd", frm.doc.notice_month);
    frm.set_df_property("notice_month_end", "reqd", frm.doc.notice_month);
  },

  before_workflow_action(frm) {
    return new Promise((resolve, reject) => {
      if (
        frm.selected_workflow_action == "Reject" &&
        frm.doc.workflow_state === "Waiting for Employee Review"
      ) {
        frappe.dom.unfreeze();
        var d = new frappe.ui.Dialog({
          title: __("Add Rejection Reason Please"),
          fields: [
            {
              label: "Rejection Reason",
              fieldname: "rejection_reason",
              fieldtype: "Small Text",
              reqd: 1,
            },
          ],
          primary_action: function () {
            var data = d.get_values();
            frappe.call({
              method: "set_rejection_reason",
              doc: frm.doc,
              args: {
                rejection_reason: data.rejection_reason,
              },
              callback: function (r) {
                if (!r.exc) {
                  if (r.message == "Done") {
                    resolve();
                  } else {
                    reject();
                  }
                  d.hide();
                } else {
                  reject();
                }
              },
            });
          },
          primary_action_label: __("Confirm"),
        });
        d.show();
      } else {
        resolve();
      }
    });
  },
});

frappe.ui.form.on("End of Service Award Deduction", {
  deduction: recalculate_on_change,
  end_of_service_award_deduction_remove: recalculate_on_change,
});

frappe.ui.form.on("End of Service Award Earning", {
  earning: recalculate_on_change,
  end_of_service_award_earning_remove: recalculate_on_change,
});
