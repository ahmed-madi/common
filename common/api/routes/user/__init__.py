from werkzeug.routing import Rule
from common.api.utils.endpoints import handle_call
from common.api.controllers.user.notification import NotificationResource
from common.api.controllers.user.dashboard import UserDashboardResource


def login():
    return handle_call("common.api.controllers.user.auth.login")


def logout():
    return handle_call("common.api.controllers.user.auth.logout")


def refresh_token():
    return handle_call("common.api.controllers.user.auth.refresh_token")


def change_user_password():
    return handle_call("common.api.controllers.user.auth.change_user_password")


user_rules = [
    Rule("/user/auth/login", methods=["POST"], endpoint=login),
    Rule("/user/auth/logout", methods=["POST"], endpoint=logout),
    Rule("/user/auth/refresh-token", methods=["POST"], endpoint=refresh_token),
    Rule("/user/change-password", methods=["PUT"], endpoint=change_user_password),
]

user_rules += NotificationResource.get_routes()
user_rules += UserDashboardResource.get_routes()
