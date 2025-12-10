import frappe
from frappe.installer import update_site_config

def update_jwt_config():
    jwt_secret_key = frappe.conf.get("encryption_key", frappe.generate_hash(length=32))
    update_site_config("jwt_secret_key", jwt_secret_key)
    update_site_config("jwt_expiry_seconds", 3600)
    update_site_config("jwt_algorithm", "HS256")
    update_site_config("jwt_refresh_expiry_seconds", 3600 * 24 * 7)
