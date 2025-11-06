frappe.ui.form.on("Project", {
  async refresh(frm) {
    const res = await fetch(
      "/api/method/frappe.core.doctype.module_def.module_def.get_installed_apps"
    );
    const data = await res.json();
    if (frm.doc.status == "Open") {
      if (data.message.includes("real_estate")) return;
      const dashboard = frm.dashboard.add_progress(
        "Project Progress",
        flt(frm.doc.percent_complete, 2),
        `${flt(frm.doc.percent_complete, 2)}% ${__("Complete")}`
      );
      customizeDashboard(frm, dashboard);
    } else {
      if (installedApps.includes("real_estate")) return;
      frm.dashboard.add_progress(
        "Project Progress",
        0,
        __(`Project is ${frm.doc.status}`)
      );
    }
  },
});

function customizeDashboard(frm, dashboard) {
  const progressArea = $(".progress-area");
  progressArea.css("position", "relative");

  let startDateTitle = `${flt(frm.doc.percent_complete, 2)}%`;
  if (frm.doc.expected_start_date) {
    startDateTitle = `${__("Start Date")}: ${frm.doc.expected_start_date}`;
  }
  const startDateToolTip = $(
    `<div style="position: absolute; top: 10px; left: 20px; font-size: 10px; font-weight:700; background: #222; color: #fff; padding: 3px 6px; border-radius: 4px">${startDateTitle}</div>`
  );

  let endDateTitle = ``;
  if (frm.doc.expected_end_date) {
    endDateTitle = `${__("End Date")}: ${frm.doc.expected_end_date}`;
  }
  const endDateToolTip = $(
    `<div style="position: absolute; bottom:35px; right: 10px; font-size: 10px; font-weight:700; background: #222; color: #fff; border-radius: 4px">${endDateTitle}</div>`
  );
  endDateTitle ? endDateToolTip.css("padding", "3px 6px") : "";

  progressArea.append(startDateToolTip);
  progressArea.append(endDateToolTip);

  if (frm.doc.custom_more_info) {
    const dashboard = frm.dashboard.add_progress(
      "Project Info",
      null,
      frm.doc.custom_more_info
    );
    const progressContainer = dashboard.find(".progress");
    progressContainer.css("display", "none");
    dashboard
      .find(".progress-message")
      .removeClass("small")
      .css("font-size", "16px")
      .css({ "font-weight": "500", "text-align": "center" });
  }
}
