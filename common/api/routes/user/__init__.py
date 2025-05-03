from werkzeug.routing import Rule
from common.api.utils.endpoints import handle_call

def login():
    return handle_call("common.api.controllers.user.login")

def logout():
    return handle_call("common.api.controllers.user.logout")

def refresh_token():
    return handle_call("common.api.controllers.user.refresh_token")

def user_info():
    return handle_call("common.api.controllers.user.user_info")


user_rules = [
	Rule("/user/auth/login", methods=["POST"], endpoint=login),
	Rule("/user/auth/logout", methods=["POST"], endpoint=logout),
	Rule("/user/auth/refresh-token", methods=["GET"], endpoint=refresh_token),
	Rule("/user/info", methods=["GET"], endpoint=user_info),
]