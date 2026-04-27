import frappe
from frappe import request

from common.api.utils.jwt import check_token_and_set_user
from common.api.utils.response import build_error_response

WHITELIST_PATHS = [
    "/api/v1/user/auth/login",
    "/api/v1/user/auth/refresh-token",
    "/api/v1/user/auth/social/providers",
    "/api/v1/user/auth/social/oauth-url",
    "/api/v1/user/auth/social/callback",
]


def before_request():
    if (
        request.path.startswith("/api/v1/")
        or request.path.startswith("/private/files/")
    ) and request.path not in WHITELIST_PATHS:
        auth_header = frappe.get_request_header("Authorization", "")
        if auth_header and auth_header.startswith("Bearer "):
            jwt_token = auth_header.split(" ")[1]
            user_d = check_token_and_set_user(jwt_token)
            if request.path.startswith("/api/v1/"):
                frappe.flags["api_call"] = True
            else:
                frappe.flags["api_call"] = False
            if not user_d:
                return
        else:
            build_error_response(
                401,
                "Authentication failed: Access token is no longer valid",
                "The provided access token is invalid",
            )
            return  # CRITICAL FIX: Stop processing unauthenticated requests
