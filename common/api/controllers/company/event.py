import frappe
from frappe.utils import cint
from common.api.utils.resource import BaseResource


class EventResource(BaseResource):
    doctype = "Event"
    url_prefix = "/company"
    resource_name = "event"
    fields = [
        "name",
        "subject",
        "published",
        "event_category",
        "color",
        "cover_image",
        "starts_on",
        "ends_on",
        "event_location",
        "event_type",
        "status",
    ]
    list_user_filters = [["published", "=", "1"]]
    list_force_user_filters = True

    @classmethod
    def get_list_filters(cls):
        filters = cls.list_user_filters.copy()
        try:
            if (
                cint(frappe.db.get_single_value("Company Policy", "active_event_only"))
                == 1
            ):
                filters.append(["status", "=", "Open"])
        except Exception:
            pass  # Fail safe if Company Policy doesn't exist or error
        return filters
