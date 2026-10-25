from werkzeug.routing import Map, Submount

from common.api.routes import url_rules


def patch_api_handle():
    """Mount the app's REST routes under /api and /api/v1.

    Only the URL map is replaced: frappe.api.handle looks API_URL_MAP up at
    call time, so the upstream handler - with its API request logging and
    monitoring - keeps serving every request.
    """
    import frappe.api
    from frappe.api.v1 import url_rules as v1_rules
    from frappe.api.v2 import url_rules as v2_rules

    if getattr(frappe.api, "_common_routes_mounted", False):
        return

    v1_rules.extend(url_rules)

    frappe.api.API_URL_MAP = Map(
        [
            # V1 routes
            Submount("/api", v1_rules),
            Submount(f"/api/{frappe.api.ApiVersion.V1.value}", v1_rules),
            Submount(f"/api/{frappe.api.ApiVersion.V2.value}", v2_rules),
        ],
        strict_slashes=False,  # Allows skipping trailing slashes
        merge_slashes=False,
    )
    frappe.api._common_routes_mounted = True
