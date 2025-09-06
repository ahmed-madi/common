from werkzeug.routing import Rule
import frappe
from common.api.utils.endpoints import handle_call
from common.api.controllers.user import notification_list

def login():
    return handle_call("common.api.controllers.user.login")

def logout():
    return handle_call("common.api.controllers.user.logout")

def refresh_token():
    return handle_call("common.api.controllers.user.refresh_token")

def user_info():
    return handle_call("common.api.controllers.user.user_info")

def change_user_password():
    return handle_call("common.api.controllers.user.change_user_password")

def employee_info(employeeId):
    frappe.form_dict.employeeId = employeeId
    return handle_call("common.api.controllers.user.employee_info")


user_rules = [
	Rule("/user/auth/login", methods=["POST"], endpoint=login),
	Rule("/user/auth/logout", methods=["POST"], endpoint=logout),
	Rule("/user/auth/refresh-token", methods=["POST"], endpoint=refresh_token),
	Rule("/user/change-password", methods=["PUT"], endpoint=change_user_password),
	Rule("/user/info", methods=["GET"], endpoint=user_info),
	Rule("/user/notifications", methods=["GET"], endpoint=notification_list),
	Rule("/user/employee-info/<path:employeeId>", methods=["GET"], endpoint=employee_info),
]