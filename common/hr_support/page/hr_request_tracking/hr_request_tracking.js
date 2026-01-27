frappe.pages['hr-request-tracking'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'HR Request Tracking',
        single_column: true
    });

    wrapper.page = page;
    new HRRequestTracking(wrapper);
}

class HRRequestTracking {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.page = wrapper.page;
        this.container = $(wrapper).find('.layout-main-section');

        this.filters = {
            tab: 'all',
            employee: '',
            doctype: '',
            from_date: '',
            to_date: '',
            page: 1,
            limit: 12
        };

        this.request_doctypes = [
            "Compensatory Leave Request", "Leave Application", "Visa Application",
            "Club Request", "Training Request", "Work From Home Request",
            "Work Outside Office Request", "Cancel Leave Application", "Leave Suspension",
            "Employee Resignation", "System Access Request", "Early Leave Application",
            "Salary Identification Letter", "Salary Fixation", "Education Allowance Request",
            "Document Request", "Change IBAN Request", "Clearance Letter Request",
            "Loan Application", "Employee Expense Request"
        ];

        this.init();
    }

    init() {
        this.render_skeleton();
        this.init_filters();
        this.bind_events();
        this.fetch_data();
    }

    render_skeleton() {
        const skeleton = `
			<div id="hr-request-tracking-container" class="hr-container">
				<div class="hr-header">
					<h2 class="hr-title">HR Request Tracking</h2>
					<div class="hr-tabs">
						<button class="hr-tab active" data-tab="all">All Requests</button>
						<button class="hr-tab" data-tab="mine">My Requests</button>
					</div>
				</div>

				<div class="hr-filters">
					<div class="hr-filter-item" id="employee-filter-container"></div>
					<div class="hr-filter-item" id="doctype-filter-container"></div>
					<div class="hr-filter-item" id="from-date-filter-container"></div>
					<div class="hr-filter-item" id="to-date-filter-container"></div>
					<div class="hr-filter-item" id="order-by-filter-container"></div>
					<div class="hr-filter-item" id="order-direction-filter-container"></div>
					<div class="hr-filter-actions">
						<button id="btn-reset-filters" class="hr-btn hr-btn-secondary">Reset</button>
						<button id="btn-apply-filters" class="hr-btn hr-btn-primary">Apply Filters</button>
					</div>
				</div>

				<div class="hr-requests-list">
					<div class="hr-list-header">
						<span>Request Type</span>
						<span>Status</span>
						<span>Request Date</span>
						<span>Employee</span>
						<span style="text-align: right;">Actions</span>
					</div>
					<div id="requests-list">
						<div class="hr-loader-container">
							<div class="hr-loader"></div>
						</div>
					</div>
				</div>

				<div id="pagination-container" class="hr-pagination"></div>
			</div>
		`;
        this.container.html(skeleton);
        this.requests_grid = this.container.find('#requests-list');
        this.pagination_container = this.container.find('#pagination-container');
    }

    init_filters() {
        const me = this;

        // 1. Employee Filter
        this.employee_filter = frappe.ui.form.make_control({
            parent: this.container.find('#employee-filter-container'),
            df: {
                fieldtype: 'Link',
                options: 'Employee',
                fieldname: 'employee',
                label: 'Employee',
                placeholder: 'Select Employee'
            },
            render_input: true,
            on_change: () => {
                me.filters.employee = me.employee_filter.get_value();
            }
        });

        // 2. Request Type (DocType) Filter
        this.doctype_filter = frappe.ui.form.make_control({
            parent: this.container.find('#doctype-filter-container'),
            df: {
                fieldtype: 'Select',
                options: ['', ...this.request_doctypes],
                fieldname: 'doctype',
                label: 'Request Type',
                placeholder: 'All Types'
            },
            render_input: true,
            on_change: () => {
                me.filters.doctype = me.doctype_filter.get_value();
            }
        });

        // 3. From Date Filter
        this.from_date_filter = frappe.ui.form.make_control({
            parent: this.container.find('#from-date-filter-container'),
            df: {
                fieldtype: 'Date',
                fieldname: 'from_date',
                label: 'From Date',
                placeholder: 'From Date'
            },
            render_input: true,
            on_change: () => {
                me.filters.from_date = me.from_date_filter.get_value();
            }
        });

        // 4. To Date Filter
        this.to_date_filter = frappe.ui.form.make_control({
            parent: this.container.find('#to-date-filter-container'),
            df: {
                fieldtype: 'Date',
                fieldname: 'to_date',
                label: 'To Date',
                placeholder: 'To Date'
            },
            render_input: true,
            on_change: () => {
                me.filters.to_date = me.to_date_filter.get_value();
            }
        });

        // 5. Order By Filter
        this.order_by_filter = frappe.ui.form.make_control({
            parent: this.container.find('#order-by-filter-container'),
            df: {
                fieldtype: 'Select',
                options: [
                    { label: 'Modified', value: 'modified' },
                    { label: 'Request Date', value: 'request_date' },
                    { label: 'Creation', value: 'creation' },
                    { label: 'Name', value: 'name' },
                    { label: 'Request Type', value: 'doctype' }
                ],
                fieldname: 'order_by',
                label: 'Sort By',
                default: 'modified'
            },
            render_input: true,
            on_change: () => {
                me.filters.order_by = me.order_by_filter.get_value();
            }
        });
        this.order_by_filter.set_value('modified');

        // 6. Order Direction Filter
        this.order_direction_filter = frappe.ui.form.make_control({
            parent: this.container.find('#order-direction-filter-container'),
            df: {
                fieldtype: 'Select',
                options: [
                    { label: 'DESC', value: 'DESC' },
                    { label: 'ASC', value: 'ASC' }
                ],
                fieldname: 'order',
                label: 'Order',
                default: 'DESC'
            },
            render_input: true,
            on_change: () => {
                me.filters.order = me.order_direction_filter.get_value();
            }
        });
        this.order_direction_filter.set_value('DESC');
    }

    bind_events() {
        const me = this;

        this.container.find('.hr-tab').on('click', function () {
            me.container.find('.hr-tab').removeClass('active');
            $(this).addClass('active');
            me.filters.tab = $(this).data('tab');
            me.filters.page = 1;

            // If "My Requests", hide employee filter
            if (me.filters.tab === 'mine') {
                me.container.find('#employee-filter-container').hide();
            } else {
                me.container.find('#employee-filter-container').show();
            }

            me.fetch_data();
        });

        this.container.find('#btn-apply-filters').on('click', () => {
            me.filters.page = 1;
            me.fetch_data();
        });

        this.container.find('#btn-reset-filters').on('click', () => {
            me.employee_filter.set_value('');
            me.doctype_filter.set_value('');
            me.from_date_filter.set_value('');
            me.to_date_filter.set_value('');
            me.order_by_filter.set_value('modified');
            me.order_direction_filter.set_value('DESC');

            me.filters.employee = '';
            me.filters.doctype = '';
            me.filters.from_date = '';
            me.filters.to_date = '';
            me.filters.order_by = 'modified';
            me.filters.order = 'DESC';
            me.filters.page = 1;
            me.fetch_data();
        });

        // Close dropdowns on outside click
        $(document).on('click', (e) => {
            if (!$(e.target).closest('.hr-card-actions').length) {
                $('.hr-dropdown-content').removeClass('show');
            }
        });
    }

    fetch_data() {
        const me = this;
        this.show_loader();

        let api_params = {
            page: this.filters.page,
            limit: this.filters.limit,
            doctype: this.filters.doctype,
            from_date: this.filters.from_date,
            to_date: this.filters.to_date,
            order: 'DESC',
            order_by: 'modified'
        };

        if (this.filters.tab === 'mine') {
            // For "My Requests", we need to get the employee ID of current user
            // We can let the backend handle it if we pass a flag, or get it here.
            // UnifiedRequestResource already has 'employee' filter.
            // Let's assume backend will handle permission/filtering if tab is 'mine'
            // Actually, let's just use the current user's employee if it exists.
            if (frappe.boot.user_info[frappe.session.user] && frappe.boot.user_info[frappe.session.user].employee) {
                api_params.employee = frappe.boot.user_info[frappe.session.user].employee;
            } else {
                // We'll try to fetch it if not in boot
                frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name').then(r => {
                    if (r && r.message) {
                        api_params.employee = r.message.name;
                        me.execute_fetch(api_params);
                    } else {
                        me.render_empty('No Employee record found for your user.');
                    }
                });
                return;
            }
        } else if (this.filters.employee) {
            api_params.employee = this.filters.employee;
        }

        this.execute_fetch(api_params);
    }

    execute_fetch(params) {
        const me = this;
        frappe.call({
            method: 'common.api.controllers.hr_requests.unified.get_unified_request_list',
            args: params,
            callback: (r) => {
                if (r.data && r.data.data_list) {
                    me.render_list(r.data.data_list);
                    me.render_pagination(r.data.totalCount);
                } else {
                    me.render_empty();
                }
            }
        });
    }

    show_loader() {
        this.requests_grid.html(`
			<div class="hr-loader-container">
				<div class="hr-loader"></div>
			</div>
		`);
        this.pagination_container.empty();
    }

    render_empty(message = 'No requests found matching your filters.') {
        this.requests_grid.html(`
			<div class="hr-empty-state">
				<p>${message}</p>
			</div>
		`);
        this.pagination_container.empty();
    }

    render_list(data) {
        const me = this;
        this.requests_grid.empty();

        if (!data || data.length === 0) {
            this.render_empty();
            return;
        }

        data.forEach(item => {
            const item_html = this.create_list_item_html(item);
            const $item = $(item_html);

            // Toggle Dropdown
            $item.find('.hr-dots-btn').on('click', function (e) {
                e.stopPropagation();
                const $dropdown = $(this).next();
                const is_showing = $dropdown.hasClass('show');

                // Close all other dropdowns and reset their row z-index
                $('.hr-dropdown-content').not($dropdown).removeClass('show');
                $('.hr-list-item').css('z-index', '');

                $dropdown.toggleClass('show');

                if (!is_showing) {
                    $(this).closest('.hr-list-item').css('z-index', '100');
                } else {
                    $(this).closest('.hr-list-item').css('z-index', '');
                }
            });

            // Bind eye icon click
            $item.find('.hr-view-btn').on('click', (e) => {
                e.stopPropagation();
                frappe.set_route('Form', item.doctype.value, item.name);
            });

            // Bind workflow actions
            $item.find('.hr-dropdown-item').on('click', function () {
                const action = $(this).data('action');
                const next_state = $(this).data('state');
                $(this).closest('.hr-dropdown-content').removeClass('show');
                me.execute_workflow_action(item.doctype.value, item.name, action, next_state);
            });

            this.requests_grid.append($item);
        });
    }

    create_list_item_html(item) {
        const status_obj = typeof item.status === 'object' ? item.status : { label: item.status, value: item.status };
        const status_val = status_obj.value || '';
        const status_label = status_obj.label || status_val;
        const status_class = this.get_status_class(status_val);

        const doctype_obj = typeof item.doctype === 'object' ? item.doctype : { label: item.doctype, value: item.doctype };
        const employee_obj = typeof item.employee === 'object' ? item.employee : { label: item.employee, value: item.employee };
        const employee_name_val = item.employee_name && typeof item.employee_name === 'object' ? item.employee_name.label : (item.employee_name || employee_obj.label || employee_obj.value || 'N/A');

        const wf_actions = item.meta_data.workflow.actions || [];

        let actions_html = '';
        wf_actions.forEach(act => {
            const action_name = act.action.value || act.action || '';
            const action_label = act.action.label || action_name;
            const next_state = act.next_state ? (act.next_state.value || act.next_state) : '';

            let btn_class = 'hr-dropdown-item';
            if (action_name.toLowerCase().includes('approve')) btn_class += ' btn-approve';
            if (action_name.toLowerCase().includes('reject')) btn_class += ' btn-reject';

            actions_html += `<button class="${btn_class}" data-action="${action_name}" data-state="${next_state}">${action_label}</button>`;
        });

        const has_actions = wf_actions.length > 0;

        return `
			<div class="hr-list-item" data-name="${item.name}">
				<div class="hr-card-doctype">${doctype_obj.label}</div>
				<div class="hr-card-status ${status_class}">${status_label}</div>
				<div class="hr-info-date">${frappe.datetime.str_to_user(item.request_date)}</div>
				<div class="hr-info-employee">${employee_name_val}</div>
				<div class="hr-list-actions">
					<button class="hr-view-btn" title="View Details">
						<i class="fa fa-eye"></i>
					</button>
					<div class="hr-card-actions">
						${has_actions ? `
						<button class="hr-dots-btn">⋮</button>
						<div class="hr-dropdown-content">
							${actions_html}
						</div>
						` : ''}
					</div>
				</div>
			</div>
		`;
    }

    get_status_class(status) {
        if (!status) return 'status-pending';
        status = String(status).toLowerCase();

        // Approved / Success (Green)
        if (status.includes('approve') || status.includes('success') || status === 'paid' || status === 'submitted' || status === 'completed') {
            return 'status-approved';
        }

        // Rejected / Error (Red)
        if (status.includes('reject') || status.includes('cancel') || status.includes('fail') || status.includes('error')) {
            return 'status-rejected';
        }

        // Waiting / Warning (Orange)
        if (status.includes('wait') || status.includes('hold') || status.includes('pending')) {
            return 'status-waiting';
        }

        // In Progress (Blue)
        if (status.includes('process') || status.includes('progress') || status === 'open') {
            return 'status-inprogress';
        }

        // Default Draft (Gray)
        return 'status-draft';
    }

    execute_workflow_action(doctype, docname, action, next_state) {
        const me = this;
        frappe.confirm(`Are you sure you want to ${action} this request?`, () => {
            frappe.call({
                method: 'common.api.controllers.common.workflow.execute_workflow_action',
                args: {
                    doctype: doctype,
                    docname: docname,
                    action: action,
                    next_state: next_state
                },
                freeze: true,
                freeze_message: 'Executing Action...',
                callback: (r) => {
                    if (r.message && r.message[0]) {
                        frappe.show_alert({ message: `Request ${action} successfully`, indicator: 'green' });
                        me.fetch_data(); // Refresh grid
                    }
                }
            });
        });
    }

    render_pagination(total) {
        const me = this;
        this.pagination_container.empty();

        const total_pages = Math.ceil(total / this.filters.limit);
        if (total_pages <= 1) return;

        const start_page = Math.max(1, this.filters.page - 2);
        const end_page = Math.min(total_pages, start_page + 4);

        // Prev
        const $prev = $(`<button class="hr-page-btn" ${this.filters.page === 1 ? 'disabled' : ''}>Prev</button>`);
        $prev.on('click', () => {
            if (me.filters.page > 1) {
                me.filters.page--;
                me.fetch_data();
            }
        });
        this.pagination_container.append($prev);

        for (let i = start_page; i <= end_page; i++) {
            const $btn = $(`<button class="hr-page-btn ${i === this.filters.page ? 'active' : ''}">${i}</button>`);
            $btn.on('click', () => {
                me.filters.page = i;
                me.fetch_data();
            });
            this.pagination_container.append($btn);
        }

        // Next
        const $next = $(`<button class="hr-page-btn" ${this.filters.page === total_pages ? 'disabled' : ''}>Next</button>`);
        $next.on('click', () => {
            if (me.filters.page < total_pages) {
                me.filters.page++;
                me.fetch_data();
            }
        });
        this.pagination_container.append($next);
    }
}
