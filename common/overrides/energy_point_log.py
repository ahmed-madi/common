import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
    get_title,
    get_title_html,
)
from frappe.utils import get_fullname
from frappe.social.doctype.energy_point_log.energy_point_log import (
    get_alert_dict,
    EnergyPointLog as BaseEnergyPointLog,
)


class EnergyPointLog(BaseEnergyPointLog):
    def after_insert(self):
        alert_dict = get_alert_dict(self)
        if alert_dict:
            frappe.publish_realtime(
                "energy_point_alert",
                message=alert_dict,
                user=self.user,
                after_commit=True,
            )

        frappe.cache.hdel("energy_points", self.user)

        if self.type != "Review" and frappe.get_cached_value(
            "Notification Settings", self.user, "energy_points_system_notifications"
        ):
            reference_user = self.user if self.type == "Auto" else self.owner
            notification_doc = {
                "type": "Energy Point",
                "document_type": self.reference_doctype,
                "document_name": self.reference_name,
                "subject": get_notification_message(self),
                "from_user": reference_user,
                "email_content": f"<div>{self.reason}</div>" if self.reason else None,
            }

            enqueue_create_notification(self.user, notification_doc)


def get_notification_message(doc):
    owner_name = get_fullname(doc.owner)
    points = doc.points
    title = get_title(doc.reference_doctype, doc.reference_name)

    if doc.type == "Auto":
        owner_name = frappe.bold("You")
        if points == 1:
            message = _("{0} gained {1} point for {2} {3}")
        else:
            message = _("{0} gained {1} points for {2} {3}")
        message = message.format(
            owner_name, frappe.bold(points), doc.rule, get_title_html(title)
        )
    elif doc.type == "Appreciation":
        if points == 1:
            message = _("{0} appreciated your work on {1} with {2} point")
        else:
            message = _("{0} appreciated your work on {1} with {2} points")
        message = message.format(
            frappe.bold(owner_name), get_title_html(title), frappe.bold(points)
        )
    elif doc.type == "Criticism":
        if points == 1:
            message = _("{0} criticized your work on {1} with {2} point")
        else:
            message = _("{0} criticized your work on {1} with {2} points")

        message = message.format(
            frappe.bold(owner_name), get_title_html(title), frappe.bold(points)
        )
    elif doc.type == "Revert":
        if points == 1:
            message = _("{0} reverted your point on {1}")
        else:
            message = _("{0} reverted your points on {1}")
        message = message.format(frappe.bold(owner_name), get_title_html(title))

    return message
