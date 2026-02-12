frappe.ui.form.on("Employee", {
    refresh(frm) {
        if (!frm.is_new()) {
            render_attendance_view(frm);
        }
    }
});

function render_attendance_view(frm) {
    const wrapper = frm.fields_dict.custom_employee_attendance.wrapper;
    $(wrapper).html(`
        <div class="text-center p-5" style="border: 1px solid #ebeef5; border-radius: 12px; background: #fff;">
            <div class="spinner-border text-primary" role="status" style="width: 2.5rem; height: 2.5rem;">
                <span class="sr-only">Loading...</span>
            </div>
            <div class="mt-3 text-muted" style="font-weight: 500;">Fetching attendance records...</div>
        </div>
    `);

    frappe.call({
        method: "common.api.employee_attendance.get_attendance_data",
        args: {
            employee: frm.doc.name
        },
        callback: function (r) {
            if (r.message) {
                const data = r.message;
                $(wrapper).empty();

                const startDate = new Date(data.start_date);
                const endDate = new Date(data.end_date);
                const daysInMonth = endDate.getDate();
                const startDay = startDate.getDay(); // 0 for Sunday

                let html = `
                    <div class="attendance-grid-container" style="padding: 20px; background: #fff; border-radius: 12px; border: 1px solid #ebeef5; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
                        <div class="header d-flex justify-content-between align-items-center mb-4">
                            <h5 style="margin: 0; font-weight: 700; color: #1a1c21; font-size: 1.1rem;">
                                <i class="fa fa-calendar-check-o" style="color: #4b66f1; margin-right: 8px;"></i> 
                                ${data.month_name}
                            </h5>
                            <div class="legend d-flex gap-3" style="font-size: 0.8rem; font-weight: 500;">
                                <div class="d-flex align-items-center"><span style="width: 10px; height: 10px; background: #28a745; border-radius: 50%; margin-right: 5px;"></span> Present</div>
                                <div class="d-flex align-items-center"><span style="width: 10px; height: 10px; background: #dc3545; border-radius: 50%; margin-right: 5px;"></span> Absent</div>
                                <div class="d-flex align-items-center"><span style="width: 10px; height: 10px; background: #fd7e14; border-radius: 50%; margin-right: 5px;"></span> Leave</div>
                                <div class="d-flex align-items-center"><span style="width: 10px; height: 10px; background: #4b66f1; border-radius: 50%; margin-right: 5px;"></span> Check-in</div>
                                <div class="d-flex align-items-center"><span style="width: 10px; height: 10px; background: #e9ecef; border-radius: 50%; margin-right: 5px;"></span> Holiday</div>
                            </div>
                        </div>
                        
                        <div class="calendar-grid" style="display: grid; grid-template-columns: repeat(7, 60px); gap: 10px; justify-content: center;">
                            ${['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => `
                                <div style="text-align: center; font-weight: 600; color: #909399; font-size: 0.75rem; text-transform: uppercase; padding-bottom: 5px;">${day}</div>
                            `).join('')}`;

                // Empty cells before start of month
                for (let i = 0; i < startDay; i++) {
                    html += `<div class="grid-cell indicator-pill no-indicator-dot whitespace-nowrap" style="width: 60px; height: 60px; background: #fcfcfd; border-radius: 8px;"></div>`;
                }

                const todayStr = frappe.datetime.nowdate();

                for (let day = 1; day <= daysInMonth; day++) {
                    const dateStr = frappe.datetime.add_days(data.start_date, day - 1);
                    const att = data.attendance.find(a => a.attendance_date === dateStr);
                    const isHoliday = data.holidays.includes(dateStr);
                    const logs = data.checkins.filter(c => c.time.startsWith(dateStr));

                    let colorClass = "";
                    let customStyle = "";

                    if (att) {
                        const greenStatuses = ['Present', 'Work From Home', 'Work Outside Office'];
                        if (greenStatuses.includes(att.status)) {
                            colorClass = "green";
                        } else if (att.status === 'Absent') {
                            colorClass = "red";
                        } else if (att.status === 'On Leave' || att.status === 'Half Day') {
                            colorClass = "orange";
                        }
                    } else if (isHoliday) {
                        colorClass = "gray";
                        customStyle = "opacity: 0.6; cursor: not-allowed; filter: grayscale(1);";
                    } else if (logs.length > 0) {
                        colorClass = "blue";
                    } else {
                        // White with gray border for missing check-in or future dates
                        colorClass = "";
                        customStyle = "background: #fff; border: 1px solid #d1d8dd !important;";
                    }

                    const tooltip = att ? att.status : (isHoliday ? 'Holiday' : (logs.length > 0 ? 'Check-in Only' : 'No Record'));
                    const logsText = logs.length > 0 ? `\nLogs: ${logs.map(l => `${l.log_type} ${l.time.substring(11, 16)}`).join(', ')}` : '';

                    html += `
                        <div class="grid-cell ${colorClass ? `indicator-pill ${colorClass} no-indicator-dot` : ''} whitespace-nowrap" 
                             title="${tooltip}${logsText}"
                             style="width: 60px; height: 60px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: all 0.2s; position: relative; border: none; margin: 0 !important; cursor: default; ${customStyle}">
                            <span style="font-size: 1rem; font-weight: 700; color: inherit;">${day}</span>
                            ${logs.length > 0 ? `
                                <div style="display: flex; gap: 2px; position: absolute; bottom: 6px;">
                                    ${logs.slice(0, 3).map(l => `<span style="width: 4px; height: 4px; border-radius: 50%; border: 1px solid #fff; background: ${l.log_type === 'IN' ? '#28a745' : '#dc3545'};" title="${l.log_type} ${l.time.substring(11, 16)}"></span>`).join('')}
                                </div>
                            ` : ''}
                        </div>`;
                }

                html += `
                        </div>
                        <style>
                            .grid-cell:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); cursor: default; }
                            .attendance-grid-container { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
                            .gap-3 { gap: 15px; }
                        </style>
                    </div>`;

                $(wrapper).html(html);
            }
        }
    });
}
