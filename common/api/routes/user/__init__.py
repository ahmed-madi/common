from werkzeug.routing import Rule
import frappe
from common.api.utils.endpoints import handle_call

def login():
    return handle_call("common.api.controllers.user.login")

def logout():
    return handle_call("common.api.controllers.user.logout")

def refresh_token():
    return handle_call("common.api.controllers.user.refresh_token")

def user_info():
    return handle_call("common.api.controllers.user.user_info")

def employee_info(employeeId):
    frappe.form_dict.employeeId = employeeId
    return handle_call("common.api.controllers.user.employee_info")


user_rules = [
	Rule("/user/auth/login", methods=["POST"], endpoint=login),
	Rule("/user/auth/logout", methods=["POST"], endpoint=logout),
	Rule("/user/auth/refresh-token", methods=["POST"], endpoint=refresh_token),
	Rule("/user/info", methods=["GET"], endpoint=user_info),
	Rule("/user/employee-info/<path:employeeId>", methods=["GET"], endpoint=employee_info),
]