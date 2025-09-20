frappe.ui.form.on("Project", {
  refresh(frm) {
    if (frm.doc.status == "Open") {
      const dashboard = frm.dashboard.add_progress(
        "Project Progress",
        flt(frm.doc.percent_complete, 2),
        `${flt(frm.doc.percent_complete, 2)}% ${__("Complete")}`
      );
      customizeDashboard(frm, dashboard);
    } else {
      frm.dashboard.add_progress(
        "Project Progress",
        0,
        __(`Project is ${frm.doc.status}`)
      );
    }
  },
});

function customizeDashboard(frm, dashboard) {
  const progressContainer = dashboard.find(".progress");
  progressContainer.css("position", "relative");

  let startDateTitle = `${flt(frm.doc.percent_complete, 2)}%`;
  if (frm.doc.expected_start_date) {
    startDateTitle = `${__("Start Date")} ${frm.doc.expected_start_date}`;
  }
  const startDateToolTip = $(
    `<div class="progress-bar" style="width:130px; background-color: transparent; margin-left: auto; position: absolute;" title="${startDateTitle}"></div>`
  ).prependTo(progressContainer);

  startDateToolTip.tooltip({
    trigger: "manual",
    placement: "top",
    customClass: "z-index-0",
  });
  startDateToolTip.tooltip("show");

  let progressContainerTitle = ``;
  if (frm.doc.expected_start_date) {
    progressContainerTitle = `${__("End Date")} ${frm.doc.expected_end_date}`;
  }
  const endDateToolTip = $(
    `<div class="progress-bar" style="width:130px; background-color: transparent; margin-left: auto; position: absolute;right: 0; left: auto;top:10px;" title="${progressContainerTitle}"></div>`
  ).appendTo(progressContainer);

  endDateToolTip.tooltip({
    trigger: "manual",
    placement: "bottom",
    customClass: "z-index-0",
  });
  endDateToolTip.tooltip("show");
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
