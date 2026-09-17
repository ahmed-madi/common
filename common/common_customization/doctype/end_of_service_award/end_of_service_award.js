// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

cur_frm.add_fetch("employee", "date_of_joining", "work_start_date");

// Each of the last month's totals and the day value it is derived from.
const MONTH_COMPONENTS = [
  ["total_month_salary", "day_value"],
  ["total_month_basic", "basic_day_value"],
  ["total_month_housing", "housing_day_value"],
  ["total_month_transportation", "transportation_day_value"],
  ["total_month_other", "other_day_value"],
];

// Some reasons - the probation period among them - have their award calculated
// and shown, but not paid. The flag is fetched from the selected reason.
function award_is_excluded(frm) {
  return cint(frm.doc.exclude_award_from_total) === 1;
}

// Number of unpaid days in the last month of service. Mirrors
// EndofServiceAward.calculate_days_number so the form and the server can never
// land on a different number - including for a service length of exactly 30
// days, where the form used to set 0 and the server the day of the end date.
async function set_days_number(frm) {
  if (!frm.doc.end_date || !frm.doc.work_start_date) {
    return;
  }

  const diff_days =
    frappe.datetime.get_diff(frm.doc.end_date, frm.doc.work_start_date) + 1;
  const days_number =
    diff_days < 30
      ? diff_days
      : frappe.datetime.str_to_obj(frm.doc.end_date).getDate();

  await frm.set_value("days_number", cint(days_number));
}

async function calculate_month_totals(frm) {
  // When the last month's salary has already been paid, every component is
  // zeroed - the journal and bank entries post from the components, not from
  // total_month_salary alone.
  if (cint(frm.doc.salary_is_already_taken)) {
    for (const [total_field] of MONTH_COMPONENTS) {
      await frm.set_value(total_field, 0);
    }
    return;
  }

  const days_number = flt(frm.doc.days_number);
  for (const [total_field, day_value_field] of MONTH_COMPONENTS) {
    await frm.set_value(
      total_field,
      flt(days_number * flt(frm.doc[day_value_field]), 2)
    );
  }
}

async function calculate_leave_cost(frm) {
  await frm.set_value(
    "leave_total_cost",
    flt(flt(frm.doc.leave_number) * flt(frm.doc.leave_cost), 2)
  );
}

async function calculate_ticket_cost(frm) {
  await frm.set_value(
    "ticket_total_cost",
    flt(flt(frm.doc.ticket_number) * flt(frm.doc.ticket_cost), 2)
  );
}

async function calculate_total_earning(frm) {
  const total = (frm.doc.end_of_service_award_earning || []).reduce(
    (sum, row) => sum + flt(row.earning),
    0
  );
  await frm.set_value("total_earning", flt(total, 2));
}

async function calculate_total_deduction(frm) {
  const total = (frm.doc.end_of_service_award_deduction || []).reduce(
    (sum, row) => sum + flt(row.deduction),
    0
  );
  await frm.set_value("total_deduction", flt(total, 2));
}

// The award comes from the formula on the selected reason, which is Python and
// so can only be evaluated on the server. The form no longer mirrors the math -
// there is one implementation, and it is the one that saves.
async function calculate_award(frm) {
  if (!frm.doc.reason) {
    await frm.set_value("award", 0);
    await frm.set_value("exclude_award_from_total", 0);
    return;
  }

  const { message } = await frappe.call({
    doc: frm.doc,
    method: "evaluate_award",
  });

  if (!message) {
    return;
  }

  await frm.set_value("award", flt(message.award, 2));
  await frm.set_value(
    "exclude_award_from_total",
    cint(message.exclude_award_from_total)
  );
}

async function calculate_total_award(frm) {
  let totals =
    flt(frm.doc.ticket_total_cost) +
    flt(frm.doc.total_month_salary) +
    flt(frm.doc.leave_total_cost) +
    flt(frm.doc.total_earning);

  // Some reasons - the probation period among them - have the award shown
  // but not paid.
  if (!award_is_excluded(frm)) {
    totals += flt(frm.doc.award);
  }

  const total_deduction = flt(frm.doc.total_deduction);
  await frm.set_value(
    "total",
    totals >= total_deduction ? flt(totals - total_deduction, 2) : 0
  );
}

// The one recalculation chain, in the same order as the server's validate().
// Every step is awaited, so no total is ever computed from a value that a
// previous step has not finished writing yet.
async function recalculate(frm, { refetch_dates = false } = {}) {
  if (refetch_dates) {
    await set_days_number(frm);
  }
  await calculate_month_totals(frm);
  await calculate_leave_cost(frm);
  await calculate_ticket_cost(frm);
  await calculate_total_earning(frm);
  await calculate_total_deduction(frm);
  await calculate_award(frm);
  await calculate_total_award(frm);
}

frappe.ui.form.on("End of Service Award", {
  onload: function (frm) {
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

  validate: function (frm) {
    return recalculate(frm);
  },

  employee: async function (frm) {
    if (!frm.doc.employee) {
      return;
    }

    const data = await frappe.call({
      method: "get_salary",
      doc: frm.doc,
      args: { employee: frm.doc.employee },
    });

    if (data && data.message) {
      await frm.set_value("salary", data.message[0]);
      await frm.set_value("day_value", data.message[1]);
      await frm.set_value("leave_cost", data.message[1]);
      await frm.set_value("basic", data.message[2]);
      await frm.set_value("basic_day_value", data.message[3]);
      await frm.set_value("housing_allowance", data.message[4]);
      await frm.set_value("housing_day_value", data.message[5]);
      await frm.set_value("transportation_allowance", data.message[6]);
      await frm.set_value("transportation_day_value", data.message[7]);
      // Other allowances are excluded from the award -temporarily-, so both the
      // allowance and its day value are forced to zero. Leaving the day value
      // populated used to leak the allowance into the journal entries while the
      // total ignored it.
      await frm.set_value("other_allowance", 0);
      await frm.set_value("other_day_value", 0);
      await frm.set_value("salary_structure", data.message[10]);
    }

    // work_start_date is fetched from the employee, so the service duration has
    // to be recomputed here too - the award is derived from years/months/days.
    await frm.trigger("get_days_months_years");
    await frm.trigger("get_leave_balance");
    await recalculate(frm, { refetch_dates: true });
  },

  end_date: async function (frm) {
    await frm.trigger("get_days_months_years");
    await frm.trigger("get_leave_balance");
    await recalculate(frm, { refetch_dates: true });
  },

  work_start_date: async function (frm) {
    await frm.trigger("get_days_months_years");
    await frm.trigger("get_leave_balance");
    await recalculate(frm, { refetch_dates: true });
  },

  // days_number stays editable so it can be overridden; changing it cascades
  // into every total that depends on it. It no longer resets
  // salary_is_already_taken - that used to silently wipe the user's choice.
  days_number: async function (frm) {
    await recalculate(frm);
  },

  salary_is_already_taken: async function (frm) {
    await recalculate(frm);
  },

  leave_number: async function (frm) {
    await recalculate(frm);
  },

  ticket_number: async function (frm) {
    await recalculate(frm);
  },

  ticket_cost: async function (frm) {
    await recalculate(frm);
  },

  reason: async function (frm) {
    await calculate_award(frm);
    await calculate_total_award(frm);
  },

  get_days_months_years: function (frm) {
    const fields = ["years", "months", "days"];
    if (!frm.doc.end_date || !frm.doc.work_start_date) {
      return Promise.all(fields.map((field) => frm.set_value(field, 0)));
    }

    if (frm.doc.end_date < frm.doc.work_start_date) {
      return Promise.all(fields.map((field) => frm.set_value(field, 0))).then(
        () => {
          frappe.throw(
            __("End date must be greater than or equal to the work start date")
          );
        }
      );
    }

    return frappe
      .call({
        method: "get_days_months_years",
        doc: frm.doc,
        args: {
          end_date: frm.doc.end_date,
          work_start_date: frm.doc.work_start_date,
        },
        freeze: true,
      })
      .then((data) => {
        const values = (data && data.message) || [0, 0, 0];
        return Promise.all(
          fields.map((field, idx) => frm.set_value(field, values[idx]))
        );
      });
  },

  get_leave_balance: function (frm) {
    if (!(frm.doc.employee && frm.doc.work_start_date && frm.doc.end_date)) {
      return frm.set_value("leave_number", 0);
    }

    return frappe
      .call({
        method: "get_leave_balance",
        doc: frm.doc,
        args: {
          employee: frm.doc.employee,
          work_start_date: frm.doc.work_start_date,
          end_date: frm.doc.end_date,
        },
        freeze: true,
      })
      .then((data) => frm.set_value("leave_number", flt(data && data.message)));
  },

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
  deduction(frm) {
    return calculate_total_deduction(frm).then(() =>
      calculate_total_award(frm)
    );
  },
  end_of_service_award_deduction_remove(frm) {
    return calculate_total_deduction(frm).then(() =>
      calculate_total_award(frm)
    );
  },
});

frappe.ui.form.on("End of Service Award Earning", {
  earning(frm) {
    return calculate_total_earning(frm).then(() => calculate_total_award(frm));
  },
  end_of_service_award_earning_remove(frm) {
    return calculate_total_earning(frm).then(() => calculate_total_award(frm));
  },
});
