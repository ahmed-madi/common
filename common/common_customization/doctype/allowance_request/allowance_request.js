// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Allowance Request", {
    refresh: function (frm) {
      if (frm.doc.docstatus == 1 && frm.doc.add_to == "Journal Entry") {
        frappe.call({
          method:
            "common_customization.common_customization.doctype.allowance_request.allowance_request.has_jv_entries",
          args: {
            name: frm.doc.name,
          },
          callback: function (r) {
            if (r.message && r.message.make_jv == 1) {
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
        if (!frm.doc.bank_entry){
          frm.add_custom_button(__("Make Bank Entry"), function () {
            return frappe.call({
              doc: frm.doc,
              method: "make_bank_entry",
              callback: function () {
                frappe.set_route("List", "Journal Entry", {
                  "Journal Entry Account.name": frm.doc.bank_entry,
                  voucher_type: "Bank Entry",
                });
              },
              freeze: true,
              freeze_message: __("Creating Payment Entries......"),
            });
          }).addClass("btn-primary");
  
        }
      }
    },
  });