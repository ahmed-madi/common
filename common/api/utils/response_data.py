import frappe
from frappe import _
from common.api.utils.workflow_handlers import WorkflowActionManager

EXTRA_DATA_MAPPER = {
    # DOCTYPE : [["cdt", "cdt_field"]]
}


def format_response_data(
    doctype, data, wf=None, add_perms=False, reqd_field=None, add_wf=False
):
    meta = frappe.get_meta(doctype)
    links, selects = get_link_fields(meta)
    title_field = meta.title_field
    roles = frappe.get_roles()
    result = []
    for row in data:
        workflow = {}
        r1 = {}
        meta_data = {"title_field": title_field}
        for k in row:
            # skip rows for read_doc
            if reqd_field and k not in reqd_field:
                continue
            # convert link, select field and title link to object with translation
            value = row[k]
            if title_field and k == title_field:
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
            r1.update(
                {
                    f"{k}": value,
                }
            )
        if not add_perms and not add_wf:
            meta_data.update({"permissions": {}, "workflow": []})
            r1.update({"meta_data": meta_data})
            result.append(r1)
            continue

        # add permissions
        doc = None
        permissions = None
        if add_perms:
            doc = frappe.get_doc(doctype, row["name"])
            permissions = frappe.permissions.get_doc_permissions(doc)
            meta_data.update(
                {"permissions": permissions or {}}
            )
        # Handle workflow actions using WorkflowActionManager
        if add_wf or wf:
            if doc is None:
                doc = frappe.get_doc(doctype, row["name"])
            if permissions is None:
                permissions = frappe.permissions.get_doc_permissions(doc)
            
            workflow_manager = WorkflowActionManager()
            workflow = workflow_manager.get_workflow_data(doc, meta, wf, permissions, roles)
        else:
            workflow = {
                "state_field": None,
                "actions": [],
            }
        meta_data.update({"workflow": workflow})
        r1.update({"meta_data": meta_data})
        result.append(r1)

    return result


def get_link_fields(meta):
    links = {}
    selects = {}
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

    return links, selects
