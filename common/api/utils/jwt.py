import jwt
import secrets
import frappe
from frappe.utils import time_diff_in_seconds, now_datetime, add_to_date
from common.api.utils.response import build_error_response

# Load JWT configuration from Frappe site config for security
# Add to site_config.json: "jwt_secret_key": "your-secure-random-key"
JWT_SECRET_KEY = frappe.conf.get("jwt_secret_key")
if not JWT_SECRET_KEY:
    # Generate a secure random key if not configured
    # WARNING: This will change on each restart. Set in site_config.json for production!
    JWT_SECRET_KEY = frappe.generate_hash(length=32)
    frappe.log_error(
        "JWT secret key not configured in site_config.json. Using temporary key.",
        "JWT Configuration Warning"
    )

JWT_ALGORITHM = frappe.conf.get("jwt_algorithm", "HS256")
JWT_EXP_DELTA_SECONDS = frappe.conf.get("jwt_expiry_seconds", 3600)  # 1 hour default
JWT_REFRESH_EXP_DELTA_SECONDS = frappe.conf.get("jwt_refresh_expiry_seconds", 3600 * 24 * 7)  # 7 days default


def generate_access_token(user_id, now, exp):
    now = now.timestamp() + JWT_EXP_DELTA_SECONDS
    payload = {
        "user_id": user_id,
        "exp": exp,
        "timestamp": now,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, JWT_ALGORITHM)


def generate_refresh_token():
    refresh_token = secrets.token_urlsafe(32)
    return refresh_token


def get_access_expiration(now):
    return add_to_date(now, seconds=JWT_EXP_DELTA_SECONDS)


def prepare_token(user):
    now = now_datetime()
    access_exp = get_access_expiration(now)
    refresh_exp = add_to_date(now, seconds=JWT_REFRESH_EXP_DELTA_SECONDS)

    refresh_token = generate_refresh_token()
    access_token = generate_access_token(user.name, now, access_exp)

    doc = frappe.new_doc("HR Auth Access Token")
    doc.user = user.name
    doc.access_token = access_token
    doc.expiration_time = access_exp
    doc.save(ignore_permissions=True)

    doc = frappe.new_doc("HR Auth Refresh Token")
    doc.user = user.name
    doc.refresh_token = refresh_token
    doc.expiration_time = refresh_exp
    doc.save(ignore_permissions=True)

    return {"access_token": access_token, "refresh_token": refresh_token}


def check_token_and_set_user(jwt_token):
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        user_id = frappe.db.exists("User", user_id)
        # Invalid User in Token!
        if not user_id:
            raise jwt.InvalidTokenError
        if frappe.db.get_value("User", user_id, "enabled") == 0:
            raise jwt.InvalidTokenError
        # Check if user has active access token
        expiration_time = frappe.db.get_value(
            "HR Auth Access Token",
            {"user": user_id, "status": "Active", "access_token": jwt_token},
            "expiration_time",
        )
        if not expiration_time:
            raise jwt.InvalidTokenError
        if time_diff_in_seconds(now_datetime(), expiration_time) > 0:
            raise jwt.ExpiredSignatureError
        frappe.set_user(user_id)
        frappe.set_user_lang(user_id, "en")
        return user_id
    except jwt.ExpiredSignatureError:
        build_error_response(
            401,
            "Authentication failed: Access token is no longer valid",
            "The provided access token is invalid",
        )
    except jwt.InvalidTokenError:
        build_error_response(
            401,
            "Authentication failed: Invalid access token provided",
            "Access token has expired",
        )
    except Exception:
        build_error_response(
            500,
            "Something went wrong on our end. Please try again later",
            "An unexpected error occurred on the server",
        )
    return None
