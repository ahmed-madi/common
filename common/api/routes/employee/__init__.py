from common.api.controllers.employee.achievement import EmployeeAchievementResource
from common.api.controllers.employee.attendance import EmployeeCheckinResource, AttendanceResource
from common.api.controllers.employee.certification import EmployeeCertificationResource
from common.api.controllers.employee.info import MyEmployeeResource, OtherEmployeeInfoResource
from common.api.controllers.employee.salary_slip import SalarySlipResource

employee_info_rules = []
employee_info_rules += EmployeeAchievementResource.get_routes()
employee_info_rules += EmployeeCheckinResource.get_routes()
employee_info_rules += AttendanceResource.get_routes()
employee_info_rules += EmployeeCertificationResource.get_routes()
employee_info_rules += MyEmployeeResource.get_routes()
employee_info_rules += OtherEmployeeInfoResource.get_routes()
employee_info_rules += SalarySlipResource.get_routes()
