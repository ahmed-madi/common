// Copyright (c) 2025, Ahmed Madi and contributors
// For license information, please see license.txt

frappe.listview_settings["HR Ticket"] = {
	has_indicator_for_draft: 1,
	get_indicator: function (doc) {
		const status_color = {
			Open: "blue",
			'On Hold': "orange",
			Resolved: "green",
			Closed: "red",
		};
		const status =
			!doc.docstatus && ["Approved", "Rejected"].includes(doc.status) ? "Draft" : doc.status;
		return [__(status), status_color[status], "status,=," + doc.status];
	},
};

