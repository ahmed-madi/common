# Common Data
from common.api.routes.common.clearance_purpose import clearance_purpose_rules
from common.api.routes.common.club import club_rules
from common.api.routes.common.company_policy import company_policy_rules
from common.api.routes.common.department import department_rules
from common.api.routes.common.employee import employee_rules
from common.api.routes.common.fiscal_year import fiscal_year_rules
from common.api.routes.common.holiday_list import holiday_list_rules
from common.api.routes.common.language import language_rules
from common.api.routes.common.leave_type import leave_type_rules
from common.api.routes.common.loan_product import loan_product_rules
from common.api.routes.common.project import project_rules
from common.api.routes.common.salary_component import salary_component_rules
from common.api.routes.common.salary_fixation_reason import salary_fixation_reason_rules
from common.api.routes.common.system_access_level import system_access_level_rules
from common.api.routes.common.work_type import work_type_rules
from common.api.routes.common.workflow import workflow_rules

# Company
from common.api.routes.company import company_rules

# Employee
from common.api.routes.employee import employee_info_rules


# Help Desk Requests
from common.api.routes.helpdesk.issue import ticket_issue_rules
from common.api.routes.helpdesk.employee_feedback import employee_feedback_rules
from common.api.routes.helpdesk.employee_inquiry import request_to_management_rules
from common.api.routes.helpdesk.ticket_comment import ticket_comment_rules
from common.api.routes.helpdesk.ticket import ticket_rules

# HR Requests
from common.api.routes.hr_requests import employee_requests_rules
from common.api.routes.hr_requests.access_system import access_system_rules
from common.api.routes.hr_requests.employee_resignation import (
    employee_resignation_rules,
)
from common.api.routes.hr_requests.expenses_request import expenses_request_rules
from common.api.routes.hr_requests.education_allowance import education_allowance_rules
from common.api.routes.hr_requests.loan import loan_rules
from common.api.routes.hr_requests.change_iban import change_iban_rules
from common.api.routes.hr_requests.clearance_letter import clearance_letter_rules
from common.api.routes.hr_requests.club_request import club_request_rules
from common.api.routes.hr_requests.document_request import document_request_rules
from common.api.routes.hr_requests.salary_fixation import salary_fixation_rules
from common.api.routes.hr_requests.salary_identification_letter import (
    salary_identification_letter_rules,
)
from common.api.routes.hr_requests.training_request import training_request_rules
from common.api.routes.hr_requests.visa_application import visa_application_rules

# Leave Requests
from common.api.routes.leave_requests.compensatory_vacation import (
    compensatory_vacation_rules,
)
from common.api.routes.leave_requests.early_leave import early_leave_rules
from common.api.routes.leave_requests.external_work import external_work_rules
from common.api.routes.leave_requests.leave_cancellation import leave_cancellation_rules
from common.api.routes.leave_requests.leave_suspension import leave_suspension_rules
from common.api.routes.leave_requests.leave import leave_application_rules
from common.api.routes.leave_requests.work_from_home import work_from_home_rules

# Project Management
from common.api.routes.project_managements.task import task_rules
from common.api.routes.project_managements.timesheet import timesheet_rules

# User Auth/Info
from common.api.routes.user import user_rules
from common.api.routes.user.firebase import firebase_rules

url_rules = []

# Common Data
url_rules += clearance_purpose_rules
url_rules += club_rules
url_rules += company_policy_rules
url_rules += department_rules
url_rules += employee_rules
url_rules += fiscal_year_rules
url_rules += holiday_list_rules
url_rules += language_rules
url_rules += leave_type_rules
url_rules += loan_product_rules
url_rules += project_rules
url_rules += salary_component_rules
url_rules += salary_fixation_reason_rules
url_rules += system_access_level_rules
url_rules += work_type_rules
url_rules += workflow_rules

# Company
url_rules += company_rules

# Employee Info Requests
url_rules += employee_info_rules

# Help Desk Requests
url_rules += ticket_issue_rules
url_rules += employee_feedback_rules
url_rules += request_to_management_rules
url_rules += ticket_comment_rules
url_rules += ticket_rules

# HR Requests
url_rules += employee_requests_rules
url_rules += access_system_rules
url_rules += employee_resignation_rules
url_rules += expenses_request_rules
url_rules += education_allowance_rules
url_rules += loan_rules
url_rules += change_iban_rules
url_rules += clearance_letter_rules
url_rules += club_request_rules
url_rules += document_request_rules
url_rules += salary_fixation_rules
url_rules += salary_identification_letter_rules
url_rules += training_request_rules
url_rules += visa_application_rules

# Leave Requests
url_rules += compensatory_vacation_rules
url_rules += early_leave_rules
url_rules += external_work_rules
url_rules += leave_cancellation_rules
url_rules += leave_suspension_rules
url_rules += leave_application_rules
url_rules += work_from_home_rules

# Project Management
url_rules += task_rules
url_rules += timesheet_rules

# User Auth/Info
url_rules += user_rules
url_rules += firebase_rules
