# Common Data
from common.api.routes.common.company_policy import company_policy_rules
from common.api.routes.common.employee import employee_rules
from common.api.routes.common.holiday_list import holiday_list_rules
from common.api.routes.common.leave_type import leave_type_rules
from common.api.routes.common.salary_component import salary_component_rules
from common.api.routes.common.work_type import work_type_rules

# Leave Requests
from common.api.routes.leave_requests.compensatory_vacation import compensatory_vacation_rules
from common.api.routes.leave_requests.early_leave import early_leave_rules
from common.api.routes.leave_requests.external_work import external_work_rules
from common.api.routes.leave_requests.leave_cancellation import leave_cancellation_rules
from common.api.routes.leave_requests.leave_suspension import leave_suspension_rules
from common.api.routes.leave_requests.leave import leave_application_rules
from common.api.routes.leave_requests.work_from_home import work_from_home_rules

# User Auth/Info
from common.api.routes.user import user_rules

url_rules = []

# Common Data
url_rules += company_policy_rules
url_rules += employee_rules
url_rules += holiday_list_rules
url_rules += leave_type_rules
url_rules += salary_component_rules
url_rules += work_type_rules

# Leave Requests
url_rules += compensatory_vacation_rules
url_rules += early_leave_rules
url_rules += external_work_rules
url_rules += leave_cancellation_rules
url_rules += leave_suspension_rules
url_rules += leave_application_rules
url_rules += work_from_home_rules

# User Auth/Info
url_rules += user_rules