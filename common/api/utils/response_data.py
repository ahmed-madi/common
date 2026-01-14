import json

import frappe
from frappe import _
from frappe.utils import get_system_timezone, strip_html
from common.api.utils.workflow_handlers import WorkflowActionManager
from common.utils import format_user_time
from common.utils.hr import get_last_checkin_status

EXTRA_DATA_MAPPER = {
    # DOCTYPE : [["cdt", "cdt_field"]]
}


def add_check_data(name):
    extra_data = {}
    last_check_in = get_last_checkin_status(name)
    extra_data.update({"checkin_status": last_check_in})
    return extra_data


def format_response_data(
    doctype,
    data,
    wf=None,
    add_perms=False,
    reqd_field=None,
    add_wf=False,
    is_for_list=False,
):
    meta = frappe.get_meta(doctype)
    links, selects, start_time = get_field_maps(meta)
    title_field = meta.title_field
    roles = frappe.get_roles()

    user_tz = (
        frappe.db.get_value("User", frappe.session.user, "time_zone")
        or get_system_timezone()
    )
    system_timezone = get_system_timezone()

    result = []
    for row in data:
        if doctype == "Employee":
            row.update(add_check_data(row["name"]))
        if doctype == "Notification Log":
            base_subject = row.get("base_subject", "") or row.get("subject", "") or ""
            base_message = (
                row.get("base_message", "") or row.get("email_content", "") or ""
            )
            context = {}
            try:
                context = json.loads(row.get("base_variables", "{}"))
            except Exception:
                context = {}
            base_subject = frappe.render_template(_(base_subject), context)
            base_message = frappe.render_template(_(base_message), context)
            row.update(
                {
                    "email_content": strip_html(base_message),
                    "subject": strip_html(base_subject),
                }
            )
            if hasattr(row, "base_variables"):
                del row["base_variables"]
            if hasattr(row, "base_message"):
                del row["base_message"]
            if hasattr(row, "base_subject"):
                del row["base_subject"]
        workflow = {
            "state_field": None,
            "actions": [],
        }
        row.update(
            {
                "doctype": {
                    "label": _(doctype),
                    "value": doctype,
                },
            }
        )
        r1 = {}
        meta_data = {"title_field": title_field}
        for k in row:
            # skip rows for read_doc
            if is_for_list and reqd_field and k not in reqd_field:
                continue
            # convert link, select field and title link to object with translation
            value = row[k]
            if title_field and k == title_field and doctype != "Notification Log":
                value = {
                    "label": _(value),
                    "value": value,
                }
            if k in links:
                link = links[k]
                label = frappe.get_meta(link["options"]).get_title_field()
                if label:
                    label = _(
                        frappe.db.get_value(link["options"], value, label) or value
                    )
                else:
                    label = _(value)
                value = {
                    "label": label,
                    "value": value,
                }
            elif k in selects:
                value = {
                    "label": _(value),
                    "value": value,
                }
            elif k in start_time:
                if value:
                    try:
                        # Datetime field
                        value = format_user_time(value, user_tz, system_timezone)
                    except Exception:
                        pass  # Keep original if conversion fails
            r1.update(
                {
                    f"{k}": value,
                }
            )
        if not add_perms and not add_wf:
            meta_data.update(
                {
                    "permissions": {},
                    "workflow": {
                        "state_field": None,
                        "actions": [],
                    },
                }
            )
            r1.update({"meta_data": meta_data})
            result.append(r1)
            continue

        # add permissions
        doc = None
        permissions = None
        if add_perms:
            doc = frappe.get_doc(doctype, row["name"])
            permissions = frappe.permissions.get_doc_permissions(doc)
            meta_data.update({"permissions": permissions or {}})
        # Handle workflow actions using WorkflowActionManager
        if add_wf or wf:
            if doc is None:
                doc = frappe.get_doc(doctype, row["name"])
            if permissions is None:
                permissions = frappe.permissions.get_doc_permissions(doc)

            workflow_manager = WorkflowActionManager()
            workflow = workflow_manager.get_workflow_data(
                doc, meta, wf, permissions, roles
            )
        else:
            workflow = {
                "state_field": None,
                "actions": [],
            }
        meta_data.update({"workflow": workflow})
        r1.update({"meta_data": meta_data})
        result.append(r1)

    return result


def get_field_maps(meta):
    links = {}
    selects = {}
    datetimes = {}

    for l_field in meta.get_link_fields():
        links.update(
            {
                f"{l_field.fieldname}": {
                    "options": l_field.options,
                    "fieldname": l_field.fieldname,
                    "type": "Link",
                },
            }
        )
    for s_field in meta.get_select_fields():
        selects.update(
            {
                f"{s_field.fieldname}": {
                    "options": s_field.options,
                    "fieldname": s_field.fieldname,
                    "type": "Select",
                },
            }
        )

    for field in meta.fields:
        if field.fieldtype in ["Datetime"]:
            datetimes[field.fieldname] = field.fieldtype

    return links, selects, datetimes
