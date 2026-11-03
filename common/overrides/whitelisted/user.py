import json

import frappe
from frappe import _
from frappe.utils import escape_html


@frappe.whitelist(methods=["POST"])
def impersonate(user: str, reason: str):
    frappe.has_permission("User", "impersonate", throw=True)

    impersonator = frappe.session.user
    frappe.get_doc(
        {
            "doctype": "Activity Log",
            "user": user,
            "status": "Success",
            "subject": _("User {0} impersonated as {1}").format(impersonator, user),
            "operation": "Impersonate",
        }
    ).insert(ignore_permissions=True, ignore_links=True)

    notification = frappe.new_doc(
        "Notification Log",
        for_user=user,
        from_user=frappe.session.user,
        subject=_("{0} just impersonated as you. They gave this reason: {1}").format(
            impersonator, reason
        ),
        email_content=None,
        base_subject="{{impersonator}} just impersonated as you. They gave this reason: {{reason}}",
        base_message=None,
        base_variables=json.dumps({"impersonator": impersonator, "reason": reason}),
    )
    notification.set("type", "Alert")
    notification.insert(ignore_permissions=True)

    # notify user via email too
    outgoing_email_exists = frappe.db.exists(
        "Email Account", {"default_outgoing": 1, "awaiting_password": 0}
    )
    if outgoing_email_exists:
        user_email = frappe.db.get_value("User", user, "email")
        email_message = _(
            "User {0} has started an impersonation session as you. <br><br><b>Reason provided:</b> {1}"
        ).format(escape_html(impersonator), escape_html(reason))

        frappe.sendmail(
            recipients=[user_email],
            subject=_("Security Alert: Your account is being impersonated"),
            content=email_message,
        )

    frappe.local.login_manager.impersonate(user)
