// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.listview_settings["Club Request"] = {
	add_fields: [
		"employee",
		"employee_name",
		"request_date",
	],
	has_indicator_for_draft: 1,
	get_indicator: function (doc) {
		const status_color = {
			Approved: "green",
			Rejected: "red",
			Open: "orange",
			Draft: "red",
			Cancelled: "red",
			Submitted: "blue",
		};
		const status =
			!doc.docstatus && ["Approved", "Rejected"].includes(doc.status) ? "Draft" : doc.status;
		return [__(status), status_color[status], "status,=," + doc.status];
	},
};