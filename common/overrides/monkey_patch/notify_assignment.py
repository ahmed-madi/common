import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
    get_title,
    get_title_html,
)


def notify_share_assignment(shared_by, doctype, doc_name, everyone, notify=0):
    if not (shared_by and doctype and doc_name) or everyone or not notify:
        return

    from frappe.utils import get_fullname

    title = get_title(doctype, doc_name)

    reference_user = get_fullname(frappe.session.user)
    notification_message = _("{0} shared a document {1} {2} with you").format(
        frappe.bold(reference_user), frappe.bold(_(doctype)), get_title_html(title)
    )

    notification_doc = {
        "type": "Share",
        "document_type": doctype,
        "subject": notification_message,
        "base_subject": "{{shared_by}} shared a document {{_(doctype)}} {{doc_name}} with you",
        "base_variables": f'{{"shared_by": "{reference_user}", "doctype": "{doctype}", "doc_name": "{doc_name}"}}',
        "document_name": doc_name,
        "from_user": frappe.session.user,
    }

    enqueue_create_notification(shared_by, notification_doc)


def notify_assignment(
    assigned_by, allocated_to, doc_type, doc_name, action="CLOSE", description=None
):
    """
    Notify assignee that there is a change in assignment
    """
    if not (assigned_by and allocated_to and doc_type and doc_name):
        return

    assigned_user = frappe.db.get_value(
        "User", allocated_to, ["language", "enabled"], as_dict=True
    )

    # return if self assigned or user disabled
    if assigned_by == allocated_to or not assigned_user.enabled:
        return

    # Search for email address in description -- i.e. assignee
    user_name = frappe.get_cached_value("User", frappe.session.user, "full_name")
    title = get_title(doc_type, doc_name)
    description_html = f"<div>{description}</div>" if description else None

    if action == "CLOSE":
        subject = _(
            "Your assignment on {0} {1} has been removed by {2}",
            lang=assigned_user.language,
        ).format(
            frappe.bold(_(doc_type)), get_title_html(title), frappe.bold(user_name)
        )
        base_subject = "Your assignment on {{_(doctype)}} {{doc_name}} has been removed by {{user_name}}"
        base_variables = f'{{"user_name": "{user_name}", "doctype": "{doc_type}", "doc_name": "{doc_name}"}}'
    else:
        user_name = frappe.bold(user_name)
        document_type = frappe.bold(_(doc_type, lang=assigned_user.language))
        title = get_title_html(title)
        subject = _(
            "{0} assigned a new task {1} {2} to you", lang=assigned_user.language
        ).format(user_name, document_type, title)
        base_subject = (
            "{{user_name}} assigned a new task {{_(doctype)}} {{doc_name}} to you"
        )
        base_variables = f'{{"user_name": "{user_name}", "doctype": "{doc_type}", "doc_name": "{doc_name}"}}'

    notification_doc = {
        "type": "Assignment",
        "document_type": doc_type,
        "subject": subject,
        "document_name": doc_name,
        "from_user": frappe.session.user,
        "email_content": description_html,
        "base_subject": base_subject,
        "base_message": "Assignment for {{doctype}} {{doc_name}}",
        "base_variables": base_variables,
    }

    enqueue_create_notification(allocated_to, notification_doc)


def patch_notify_assignment():
    import frappe.share
    import frappe.desk.form.assign_to

    frappe.share.notify_assignment = notify_share_assignment
    frappe.desk.form.assign_to.notify_assignment = notify_assignment
