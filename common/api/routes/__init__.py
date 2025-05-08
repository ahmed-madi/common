# Common Data
from common.api.routes.common.company_policy import company_policy_rules
from common.api.routes.common.employee import employee_rules
from common.api.routes.common.holiday_list import holiday_list_rules
from common.api.routes.common.leave_type import leave_type_rules
from common.api.routes.common.salary_component import salary_component_rules
from common.api.routes.common.work_type import work_type_rules

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

# User Auth/Info
url_rules += user_rules