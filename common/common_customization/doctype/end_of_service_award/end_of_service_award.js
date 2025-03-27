// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

cur_frm.add_fetch("employee", "date_of_joining", "work_start_date");

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
  salary_is_already_taken(frm) {
    if (frm.doc.salary_is_already_taken) {
      frm.set_value("total_month_salary", 0);
      // frm.toggle_enable("total_month_salary", false);
    } else {
      // frm.toggle_enable("total_month_salary", true);
      frm.set_value(
        "total_month_salary",
        flt(frm.doc.days_number) * flt(frm.doc.day_value)
      );
    }
  },
  days_number(frm) {
    const days_number = cint(frm.doc.days_number);
    frm.set_value("days_number", days_number).then(() => {
      frm.trigger("recalculate_totals_in_salary").then(() => {
        frm.trigger("calculate_total_award");
      });
    });
  },
  recalculate_totals_in_salary(frm) {
    frm.set_value("salary_is_already_taken", 0);
    frm.set_value(
      "total_month_salary",
      frm.doc.days_number * frm.doc.day_value
    );

    frm.set_value(
      "total_month_basic",
      frm.doc.days_number * frm.doc.basic_day_value
    );
    frm.set_value(
      "total_month_housing",
      frm.doc.days_number * frm.doc.housing_day_value
    );
    frm.set_value(
      "total_month_transportation",
      frm.doc.days_number * frm.doc.transportation_day_value
    );
    frm.set_value(
      "total_month_other",
      frm.doc.days_number * frm.doc.other_day_value
    );
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
  notice_month: function (frm) {
    frm.set_df_property("notice_month_start", "reqd", frm.doc.notice_month);
    frm.set_df_property("notice_month_end", "reqd", frm.doc.notice_month);
  },

  employee: function (frm) {
    if (frm.doc.employee) {
      frappe.call({
        method: "get_salary",
        doc: frm.doc,
        args: { employee: frm.doc.employee },
        callback: async function (data) {
          if (data) {
            await frm.set_value("salary", data.message[0]);
            await frm.set_value("day_value", data.message[1]);
            await frm.set_value("leave_cost", data.message[1]);

            await frm.trigger("get_leave_balance");
            await frm.set_value(
              "leave_total_cost",
              Math.round(frm.doc.leave_number * frm.doc.leave_cost)
            );
            await frm.set_value("basic", data.message[2]);
            await frm.set_value("basic_day_value", data.message[3]);
            await frm.set_value("housing_allowance", data.message[4]);
            await frm.set_value("housing_day_value", data.message[5]);
            await frm.set_value("transportation_allowance", data.message[6]);
            await frm.set_value("transportation_day_value", data.message[7]);
            await frm.set_value(
              "other_allowance",
              0 /*data.message[8] -temporarily set as zero- */
            );
            await frm.set_value("other_day_value", data.message[9]);
            await frm.set_value("salary_structure", data.message[10]);
          }
          await frm.trigger("get_award");
          await frm.trigger("calculate_total_award");
        },
      });
    }

    if (frm.doc.employee && frm.doc.end_date) {
      var end_resignation_date = new Date(frm.doc.end_date);

      var date1 = new Date(frm.doc.work_start_date);
      var date2 = new Date(frm.doc.end_date);
      var diffTime = date2.getTime() - date1.getTime();
      var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

      if (diffDays < 30) {
        frm.set_value("days_number", diffDays);
      } else if (diffDays == 30) {
        frm.set_value("days_number", 0);
      } else {
        frm.set_value("days_number", end_resignation_date.getDate());
      }
      frm.set_value("salary_is_already_taken", 0);
      frm.set_value(
        "total_month_salary",
        frm.doc.days_number * frm.doc.day_value
      );

      frm.set_value(
        "total_month_basic",
        frm.doc.days_number * frm.doc.basic_day_value
      );
      frm.set_value(
        "total_month_housing",
        frm.doc.days_number * frm.doc.housing_day_value
      );
      frm.set_value(
        "total_month_transportation",
        frm.doc.days_number * frm.doc.transportation_day_value
      );
      frm.set_value(
        "total_month_other",
        frm.doc.days_number * frm.doc.other_day_value
      );
      frm.trigger("calculate_total_award");
    }
  },

  total_month_salary(frm) {
    frm.trigger("calculate_total_award");
  },
  leave_total_cost(frm) {
    frm.trigger("calculate_total_award");
  },
  ticket_total_cost(frm) {
    frm.trigger("calculate_total_award");
  },
  reason(frm) {
    frm.trigger("calculate_total_award");
  },
  end_date: async function (frm) {
    await frm.trigger("get_leave_balance");
    await frm.trigger("get_days_months_years");

    if (frm.doc.employee && frm.doc.end_date) {
      var end_resignation_date = new Date(frm.doc.end_date);

      var date1 = new Date(frm.doc.work_start_date);
      var date2 = new Date(frm.doc.end_date);
      var diffTime = Math.abs(date2 - date1);
      var diffDays = Math.ceil(diffTime / (1000 * 3600 * 24)) + 1;

      if (diffDays < 30) {
        await frm.set_value("days_number", diffDays);
      } else if (diffDays == 30) {
        frm.set_value("days_number", 0);
      } else {
        await frm.set_value("days_number", end_resignation_date.getDate());
      }

      await frm.set_value("salary_is_already_taken", 0);
      await frm.set_value(
        "total_month_salary",
        frm.doc.days_number * frm.doc.day_value
      );
      await frm.set_value(
        "total_month_basic",
        frm.doc.days_number * frm.doc.basic_day_value
      );
      await frm.set_value(
        "total_month_housing",
        frm.doc.days_number * frm.doc.housing_day_value
      );
      await frm.set_value(
        "total_month_transportation",
        frm.doc.days_number * frm.doc.transportation_day_value
      );
      await frm.set_value(
        "total_month_other",
        frm.doc.days_number * frm.doc.other_day_value
      );
      await frm.trigger("calculate_total_award");
    }
  },
  work_start_date(frm) {
    frm.trigger("get_days_months_years");
  },
  get_days_months_years(frm) {
    const fields = ["years", "months", "days"];
    if (!frm.doc.end_date || !frm.doc.work_start_date) {
      fields.forEach((field) => frm.set_value(field, 0));
      frm.trigger("get_award");
      return;
    }
    if (frm.doc.end_date < frm.doc.work_start_date) {
      fields.forEach((field) => frm.set_value(field, 0));
      frm.trigger("get_award");
      frappe.throw("تاريخ نهاية العمل يجب أن يكون أكبر من تاريخ بداية العمل");
    } else {
      frappe.call({
        method: "get_days_months_years",
        doc: frm.doc,
        args: {
          end_date: frm.doc.end_date,
          work_start_date: frm.doc.work_start_date,
        },
        freeze: true,
        callback: function (data) {
          if (data) {
            fields.forEach((field, idx) =>
              frm.set_value(field, data.message[idx])
            );
          } else {
            fields.forEach((field) => frm.set_value(field, 0));
          }
          frm.trigger("get_award");
        },
      });
    }
  },

  validate: function (frm) {
    frm.trigger("calculate_total_deduction");
    frm.trigger("calculate_total_earning");
    frm.trigger("get_award");
    frm.trigger("calculate_total_award");
  },

  get_award: function (frm) {
    var result = 0;
    frm.set_value("award", 0);
    if (!frm.doc.reason) {
      frappe.show_alert(
        {
          message: __("أرجو اختيار سبب نهاية الخدمة"),
          indicator: "red",
        },
        5
      );
      frm.trigger("calculate_total_award");
      return;
    }
    const salary = flt(frm.doc.salary);
    var years =
      cint(frm.doc.years) +
      cint(frm.doc.months) / 12 +
      cint(frm.doc.days) / 360;

    if (!frm.doc.reason) {
      frappe.show_alert(
        {
          message: __("أرجو اختيار سبب نهاية الخدمة"),
          indicator: "red",
        },
        5
      );
      frm.trigger("calculate_total_award");
      frm.set_value("award", 0);
    } else {
      if (
        frm.doc.reason ==
        "انتهاء مدة العقد أو الاتفاق بين الطرفين على انهاء العقد أو انهاء العقد من قبل الشركة"
      ) {
        // frm.set_value('award', "");
        var firstPeriod,
          secondPeriod = 0;
        // set periods
        if (years > 5) {
          firstPeriod = 5;
          secondPeriod = years - 5;
        } else {
          firstPeriod = years;
        }
        // calculate
        result = firstPeriod * salary * 0.5 + secondPeriod * salary;
        frm.set_value("award", Math.round(result * 100) / 100);
      } else {
        if (frm.doc.reason == "") {
          frm.set_value("award", 0);
        } else if (frm.doc.reason == "استقالة الموظف قبل انتهاء مدة العقد") {
          if (years < 2) {
            result = 0;
          } else if (years <= 5) {
            result = (1 / 6) * salary * years;
          } else if (years <= 10) {
            result = (1 / 3) * salary * 5 + (2 / 3) * salary * (years - 5);
          } else {
            result = 0.5 * salary * 5 + salary * (years - 5);
          }
          if (typeof result === "number") {
            frm.set_value("award", Math.round(result * 100) / 100);
          } else {
            frm.set_value("award", Math.round(result * 100) / 100);
          }
        } else {
          if (years <= 5) {
            result = 0.5 * salary * years;
          } else {
            result = 0.5 * salary * 5 + salary * (years - 5);
          }
          if (typeof result === "number") {
            frm.set_value("award", Math.round(result * 100) / 100);
          } else {
            frm.set_value("award", Math.round(result * 100) / 100);
          }
        }
      }
    }
    frm.trigger("calculate_total_award");
  },

  // Done!
  after_save(frm) {
    frm.trigger("calculate_total_award");
  },

  get_leave_balance(frm) {
    frm.set_value("leave_number", 0);
    frm.set_value("leave_total_cost", 0);
    if (frm.doc.employee && frm.doc.work_start_date && frm.doc.end_date) {
      frappe.call({
        method: "get_leave_balance",
        doc: frm.doc,
        args: {
          employee: frm.doc.employee,
          work_start_date: frm.doc.work_start_date,
          end_date: frm.doc.end_date,
        },
        freeze: true,
        callback: function (data) {
          if (data) {
            frm.set_value("leave_number", data.message);
            frm
              .set_value(
                "leave_total_cost",
                Math.round(data.message * frm.doc.leave_cost)
              )
              .then(() => {
                frm.trigger("calculate_total_award");
              });
          }
          frm.trigger("calculate_total_award");
        },
      });
    } else {
      frm.trigger("calculate_total_award");
    }
  },
  leave_number(frm) {
    frm.set_value(
      "leave_total_cost",
      Math.round(flt(frm.doc.leave_number) * flt(frm.doc.leave_cost))
    );
    frm.trigger("calculate_total_award");
  },
  ticket_number(frm) {
    frm.trigger("calculate_total_ticket_cost");
  },
  ticket_cost(frm) {
    frm.trigger("calculate_total_ticket_cost");
  },
  calculate_total_deduction(frm) {
    const total = (frm.doc.end_of_service_award_deduction || []).reduce(
      (prev, curr) => parseFloat(curr.deduction) + prev,
      0
    );
    frm.set_value("total_deduction", total);
  },

  calculate_total_salary(frm) {},
  calculate_total_earning(frm) {
    const total = (frm.doc.end_of_service_award_earning || []).reduce(
      (prev, curr) => parseFloat(curr.earning) + prev,
      0
    );
    frm.set_value("total_earning", total);
  },

  calculate_total_ticket_cost(frm) {
    if (frm.doc.ticket_number && frm.doc.ticket_cost) {
      frm.set_value(
        "ticket_total_cost",
        frm.doc.ticket_number * frm.doc.ticket_cost
      );
    } else {
      frm.set_value("ticket_total_cost", 0);
    }
    frm.trigger("calculate_total_award");
  },
  calculate_total_award(frm) {
    if (frm.doc.reason === "انهاء العقد خلال فتره التجربه") {
      const totals =
        flt(frm.doc.ticket_total_cost) +
        (frm.doc.salary_is_already_taken == 1
          ? 0
          : flt(frm.doc.total_month_salary)) +
        flt(frm.doc.leave_total_cost) +
        flt(frm.doc.total_earning);

      frm.set_value(
        "total",
        totals >= flt(frm.doc.total_deduction)
          ? totals - flt(frm.doc.total_deduction)
          : 0
      );
    } else {
      const totals =
        flt(frm.doc.award) +
        flt(frm.doc.ticket_total_cost) +
        flt(frm.doc.total_month_salary) +
        flt(frm.doc.leave_total_cost) +
        flt(frm.doc.total_earning);

      frm.set_value(
        "total",
        totals >= flt(frm.doc.total_deduction)
          ? totals - flt(frm.doc.total_deduction)
          : 0
      );
    }
  },
});

frappe.ui.form.on("End of Service Award Deduction", {
  deduction(frm, cdt, cdn) {
    frm.trigger("calculate_total_deduction");
    frm.trigger("calculate_total_award");
  },
  end_of_service_award_deduction_remove(frm, cdt, cdn) {
    frm.trigger("calculate_total_deduction");
    frm.trigger("calculate_total_award");
  },
});
frappe.ui.form.on("End of Service Award Earning", {
  earning(frm, cdt, cdn) {
    frm.trigger("calculate_total_earning");
    frm.trigger("calculate_total_award");
  },
  end_of_service_award_earning_remove(frm, cdt, cdn) {
    frm.trigger("calculate_total_earning");
    frm.trigger("calculate_total_award");
  },
});
