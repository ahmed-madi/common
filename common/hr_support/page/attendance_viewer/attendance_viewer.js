frappe.pages['attendance-viewer'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Employee Attendance',
		single_column: true
	});

	new AttendanceViewer(wrapper);
}

class AttendanceViewer {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.container = $(wrapper).find('.layout-main-section');

		this.filters = {
			year: moment().year().toString(),
			month: moment().month() + 1,
			search: '',
			start: 0,
			page_length: 10
		};

		this.data = {
			employees: [],
			total_count: 0
		};

		this.init();
	}

	init() {
		this.load_assets();
		this.render_skeleton();
	}

	load_assets() {
		frappe.require('assets/common/hr_support/page/attendance_viewer/attendance_viewer.css');
	}

	render_skeleton() {
		const skeleton = `
            <div class="attendance-viewer-container">
                <div class="viewer-header">
                    <h3 id="page-title">Employee Attendance</h3>
                    <div class="viewer-filters">
                        <div id="search-filter" class="filter-item"></div>
                        <div id="year-filter" class="filter-item"></div>
                        <div id="month-filter" class="filter-item"></div>
                    </div>
                </div>

                <div id="attendance-list" class="employee-grid">
                    <!-- Cards will be injected here -->
                </div>

                <div class="pagination-section text-center p-4">
                    <button id="btn-load-more" class="btn btn-default btn-sm hide">Load More</button>
                    <div id="pagination-info" class="text-muted small mt-2"></div>
                </div>
            </div>
        `;
		this.container.html(skeleton);
		this.list_container = this.container.find('#attendance-list');

		setTimeout(() => {
			this.init_filters();
			this.fetch_data();
		}, 100);
	}

	init_filters() {
		const me = this;

		const $year = this.container.find('#year-filter');
		const $month = this.container.find('#month-filter');
		const $search = this.container.find('#search-filter');

		if (!$year.length || !$month.length || !$search.length) return;

		// Search Filter
		this.search_filter = frappe.ui.form.make_control({
			parent: $search,
			df: {
				fieldtype: 'Data',
				fieldname: 'search',
				label: 'Search',
				placeholder: 'Name, ID, or Designation...',
				on_change: () => {
					me.filters.search = me.search_filter.get_value();
					me.refresh_data();
				}
			},
			render_input: true
		});

		this.year_filter = frappe.ui.form.make_control({
			parent: $year,
			df: {
				fieldtype: 'Link',
				options: 'Fiscal Year',
				fieldname: 'year',
				label: 'Fiscal Year',
				placeholder: 'Select Year',
				on_change: () => {
					me.filters.year = me.year_filter.get_value();
					me.refresh_data();
				}
			},
			render_input: true
		});

		this.month_filter = frappe.ui.form.make_control({
			parent: $month,
			df: {
				fieldtype: 'Select',
				options: [
					{ label: 'January', value: 1 },
					{ label: 'February', value: 2 },
					{ label: 'March', value: 3 },
					{ label: 'April', value: 4 },
					{ label: 'May', value: 5 },
					{ label: 'June', value: 6 },
					{ label: 'July', value: 7 },
					{ label: 'August', value: 8 },
					{ label: 'September', value: 9 },
					{ label: 'October', value: 10 },
					{ label: 'November', value: 11 },
					{ label: 'December', value: 12 }
				],
				fieldname: 'month',
				label: 'Month',
				on_change: () => {
					me.filters.month = me.month_filter.get_value();
					me.refresh_data();
				}
			},
			render_input: true
		});

		this.year_filter.set_value(this.filters.year, false);
		this.month_filter.set_value(this.filters.month, false);

		// Bind Load More
		this.container.on('click', '#btn-load-more', () => {
			me.filters.start += me.filters.page_length;
			me.fetch_data(true);
		});

		// Search input debounce/trigger
		this.search_filter.$input.on('keypress', (e) => {
			if (e.which == 13) {
				me.filters.search = me.search_filter.get_value();
				me.refresh_data();
			}
		});
	}

	refresh_data() {
		this.filters.start = 0;
		this.data.employees = [];
		this.list_container.empty();
		this.fetch_data();
	}

	fetch_data(append = false) {
		const me = this;
		if (!append) this.show_loader();

		frappe.call({
			method: 'common.api.attendance_viewer.get_attendance_summary',
			args: {
				year: this.filters.year,
				month: this.filters.month,
				search: this.filters.search,
				start: this.filters.start,
				page_length: this.filters.page_length
			},
			callback: (r) => {
				if (r.message) {
					if (append) {
						me.data.employees = me.data.employees.concat(r.message.employees);
					} else {
						me.data.employees = r.message.employees;
						me.list_container.empty();
					}
					me.data.total_count = r.message.total_count;
					me.render_list(r.message, append);
				}
			}
		});
	}

	show_loader() {
		if (this.list_container) {
			this.list_container.html(`
				<div class="loader-container">
					<div class="loader"></div>
				</div>
			`);
		}
	}

	render_list(message, append = false) {
		const me = this;
		const employees = message.employees;

		if (!append && (!employees || employees.length === 0)) {
			this.list_container.html('<div class="text-center p-5">No active employees found matching the filters.</div>');
			this.container.find('#btn-load-more').addClass('hide');
			this.container.find('#pagination-info').text('');
			return;
		}

		employees.forEach(emp => {
			const card = this.create_card(emp, message.start_date);
			this.list_container.append(card);
		});

		// Update Pagination controls
		const loaded = this.filters.start + employees.length;
		const total = message.total_count;

		if (loaded < total) {
			this.container.find('#btn-load-more').removeClass('hide');
		} else {
			this.container.find('#btn-load-more').addClass('hide');
		}

		this.container.find('#pagination-info').text(`Showing ${loaded} of ${total} employees`);
	}

	format_hours(hours) {
		const h = Math.floor(hours);
		const m = Math.round((hours - h) * 60);
		return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
	}

	get_abbr(name) {
		if (!name) return '??';
		return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
	}

	create_card(emp, start_date) {
		const me = this;
		const avatar_url = emp.image;

		const date_obj = moment(start_date);
		const firstDayWeekday = date_obj.day();
		const offset = firstDayWeekday;

		let empty_cells = '';
		for (let i = 0; i < offset; i++) {
			empty_cells += '<div class="day-cell day-empty"></div>';
		}

		const days_html = emp.daily_status.map((d, i) => {
			const day = moment(d.date).date();
			return `<div class="day-cell day-${d.status}">${day.toString().padStart(2, '0')}</div>`;
		}).join('');

		const avatar_html = avatar_url ?
			`<img src="${avatar_url}" class="avatar-image" alt="${emp.employee_name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
             <div class="avatar-placeholder" style="display:none;">${this.get_abbr(emp.employee_name)}</div>` :
			`<div class="avatar-placeholder">${this.get_abbr(emp.employee_name)}</div>`;

		const html = `
			<div class="attendance-card">
                <div class="card-actions">
                    <button class="action-btn check"><i class="fa fa-check"></i></button>
                    <button class="action-btn view" onclick="frappe.set_route('Form', 'Employee', '${emp.employee}')"><i class="fa fa-eye"></i></button>
                </div>

                <div class="calendar-section">
                    <div class="days-header">
                        <span>SAT</span><span>FRI</span><span>THU</span><span>WED</span><span>TUE</span><span>MON</span><span>SUN</span>
                    </div>
                    <div class="days-grid">
                        ${empty_cells}
                        ${days_html}
                    </div>
                </div>


                <div class="stats-section">
					<div class="stat-item">
                        <span class="stat-value text-primary">${this.format_hours(emp.scheduled_hours)}</span>
                        <span class="stat-label">Scheduled</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value text-success">${this.format_hours(emp.actual_hours)}</span>
                        <span class="stat-label">Actual</span>
                    </div>
					<div class="stat-item">
                        <span class="stat-value ${flt(emp.difference) < 0 ? 'text-danger' : ''}">${this.format_hours(Math.abs(flt(emp.difference)))}</span>
                        <span class="stat-label">Difference</span>
                    </div>
                </div>

                <div class="profile-section">
                    <div class="avatar-wrapper">
                        ${avatar_html}
                        <div class="status-indicator"></div>
                    </div>
                    <div class="emp-name" title="${emp.employee_name}">${emp.employee_name}</div>
                    <div class="emp-designation">${emp.designation || 'N/A'}</div>
                </div>
			</div>
		`;
		return html;
	}
}