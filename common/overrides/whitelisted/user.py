import frappe
from frappe import _


@frappe.whitelist(methods=["POST"])
def impersonate(user: str, reason: str):
    # Note: For now we only allow admins, we MIGHT allow system manager in future.
    # All the impersonation code doesn't assume anything about user.
    frappe.only_for("Administrator")

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
        base_variables=f'{{"impersonator": "{impersonator}", "reason": "{reason}"}}',
    )
    notification.set("type", "Alert")
    notification.insert(ignore_permissions=True)
    frappe.local.login_manager.impersonate(user)
