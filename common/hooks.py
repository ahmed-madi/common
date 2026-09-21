app_name = "common"
app_title = "Common Customization"
app_publisher = "Ahmed Madi"
app_description = "Common customization"
app_email = "dev.amadi7@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "common",
# 		"logo": "/assets/common/logo.png",
# 		"title": "Common Customization",
# 		"route": "/common",
# 		"has_permission": "common.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
    "/assets/common/css/common-style3.css",
]
app_include_js = "/assets/common/js/form_timeline_workflow.js"

# include js, css files in header of web template
# web_include_css = "/assets/common/css/common.css"
# web_include_js = "/assets/common/js/common.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "common/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
    "Employee": "public/js/employee.js",
}
doctype_list_js = {
    "Attendance": "public/js/attendance_list.js",
    "Project": "public/js/project.js",
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
app_include_icons = ["common/icons/palm_tree.svg"]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
    "methods": [
        "common.common_customization.doctype.salary_identification_letter.letter.get_letter_context",
    ]
}

# Installation
# ------------

# before_install = "common.install.before_install"
after_install = "common.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "common.uninstall.before_uninstall"
# after_uninstall = "common.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "common.utils.before_app_install"
# after_app_install = "common.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "common.utils.before_app_uninstall"
# after_app_uninstall = "common.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "common.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
    "Employee HR Feedback": "common.permissions.employee_hr_feedback.get_permission_query_conditions",
}

has_permission = {
    "Employee HR Feedback": "common.permissions.employee_hr_feedback.has_permission",
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Leave Application": "common.overrides.leave_application.LeaveApplication",
    "Leave Type": "common.overrides.leave_type.LeaveType",
    "Compensatory Leave Request": "common.overrides.compensatory_leave_request.CompensatoryLeaveRequest",
    "Loan Application": "common.overrides.loan_application.LoanApplication",
    "Notification": "common.overrides.notification.Notification",
    "Notification Log": "common.overrides.notification.NotificationLog",
    "Employee Checkin": "common.overrides.employee_checkin.EmployeeCheckin",
    "Reminder": "common.overrides.reminder.Reminder",
    "Submission Queue": "common.overrides.submission_queue.SubmissionQueue",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Employee": {"after_insert": "common.overrides.employee.after_insert"},
    "Company": {
        "after_insert": "common.events.company.after_insert",
        "on_update": "common.events.company.on_update",
    },
    "Task": {
        "on_update": "common.events.task.on_update",
    },
    # The Employee carries its salary and leave balance, refreshed by every
    # document that can change either of them - on cancel as well as on submit.
    "Salary Slip": {
        "on_submit": "common.events.employee_snapshot.on_salary_slip_change",
        "on_cancel": "common.events.employee_snapshot.on_salary_slip_change",
    },
    "Leave Application": {
        "on_submit": "common.events.employee_snapshot.on_leave_change",
        "on_cancel": "common.events.employee_snapshot.on_leave_change",
    },
    "Leave Allocation": {
        "on_submit": "common.events.employee_snapshot.on_leave_change",
        "on_cancel": "common.events.employee_snapshot.on_leave_change",
    },
}

# Additional Timeline Content
# ---------------------------
# Add custom content to form timeline

additional_timeline_content = {
    "*": ["common.overrides.form_load.get_workflow_actions_timeline_content"],
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"common.tasks.all"
# 	],
# 	"daily": [
# 		"common.tasks.daily"
# 	],
# 	"hourly": [
# 		"common.tasks.hourly"
# 	],
# 	"weekly": [
# 		"common.tasks.weekly"
# 	],
# 	"monthly": [
# 		"common.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "common.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
    "frappe.core.doctype.user.user.impersonate": "common.overrides.whitelisted.user.impersonate",
    "frappe.integrations.oauth2_logins.login_via_google": "common.overrides.whitelisted.oauth2_logins.login_via_google",
    "frappe.integrations.oauth2_logins.login_via_github": "common.overrides.whitelisted.oauth2_logins.login_via_github",
    "frappe.integrations.oauth2_logins.login_via_facebook": "common.overrides.whitelisted.oauth2_logins.login_via_facebook",
    "frappe.integrations.oauth2_logins.login_via_frappe": "common.overrides.whitelisted.oauth2_logins.login_via_frappe",
    "frappe.integrations.oauth2_logins.login_via_office365": "common.overrides.whitelisted.oauth2_logins.login_via_office365",
    "frappe.integrations.oauth2_logins.login_via_salesforce": "common.overrides.whitelisted.oauth2_logins.login_via_salesforce",
    "frappe.integrations.oauth2_logins.login_via_fairlogin": "common.overrides.whitelisted.oauth2_logins.login_via_fairlogin",
    "frappe.integrations.oauth2_logins.login_via_keycloak": "common.overrides.whitelisted.oauth2_logins.login_via_keycloak",
    "frappe.integrations.oauth2_logins.custom": "common.overrides.whitelisted.oauth2_logins.custom",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "common.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["common.api.utils.request.before_request"]
# after_request = ["common.utils.after_request"]

# Job Events
# ----------
# before_job = ["common.utils.before_job"]
# after_job = ["common.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"common.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

website_route_rules = [
    {"from_route": "/hr-services/<path:app_path>", "to_route": "hr_service"},
]


fixtures = [
    {"dt": "Workflow", "filters": [["name", "in", ["Task"]]]},
    {
        "dt": "Workflow State",
        "filters": [
            [
                "name",
                "in",
                ["Open", "In Progress", "Completed", "Pending Review", "Re-Open"],
            ]
        ],
    },
    {
        "dt": "Workflow Action Master",
        "filters": [
            [
                "name",
                "in",
                ["Start", "Review", "Approve", "Re-Open"],
            ]
        ],
    },
]
