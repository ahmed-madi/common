import frappe
from frappe import _


def is_condition_satisfied(transition, doc):
    if not transition.condition:
        return True
    try:
        return frappe.safe_eval(transition.condition, None, dict(doc=doc.as_dict()))
    except Exception:
        return False


def get_state_journey(doctype, docname, state_field, workflow):
    """
    Fetch all workflow states and mark them as past, current, or future.
    Filters future states based on reachability and conditions.
    """
    try:
        doc = frappe.get_doc(doctype, docname)
    except Exception:
        return []

    all_states_list = []
    for s in workflow.states:
        if s.state and s.state not in all_states_list:
            all_states_list.append(s.state)

    current_state = doc.get(state_field)

    # 1. Get visited states and completing users
    state_to_user = {}

    # Check Workflow Action records for "Completed" actions
    workflow_actions = frappe.get_all(
        "Workflow Action",
        filters={
            "reference_doctype": doctype,
            "reference_name": docname,
            "status": "Completed",
        },
        fields=["workflow_state", "completed_by", "creation"],
    )
    for wa in workflow_actions:
        if wa.workflow_state and wa.completed_by:
            state_to_user[wa.workflow_state] = {
                "user": wa.completed_by,
                "time": wa.creation,
            }

    # Check Version history for field changes
    versions = frappe.get_all(
        "Version",
        filters={"ref_doctype": doctype, "docname": docname},
        fields=["data", "owner", "creation"],
    )
    for v in versions:
        try:
            import json

            data = json.loads(v.data)
            changed = data.get("changed", [])
            for change in changed:
                if change[0] == state_field:
                    # change[2] is the New Value (the state transitioned TO)
                    state_to_user[change[2]] = {"user": v.owner, "time": v.creation}
        except Exception:
            continue

    # The current state is always considered "visited" even if not in logs yet
    visited_states_keys = list(state_to_user.keys())
    if current_state and current_state not in visited_states_keys:
        visited_states_keys.append(current_state)

    # 2. Reachability Analysis (BFS) to find reachable future states
    reachable_future_states = []
    if current_state:
        queue = [current_state]
        visited_in_bfs = {current_state}
        while queue:
            node = queue.pop(0)
            if node != current_state:
                reachable_future_states.append(node)

            for transition in workflow.transitions:
                if transition.state == node and is_condition_satisfied(transition, doc):
                    if transition.next_state not in visited_in_bfs:
                        visited_in_bfs.add(transition.next_state)
                        queue.append(transition.next_state)

    def get_user_details(user_ids):
        if not user_ids:
            return []

        user_data = frappe.get_all(
            "User",
            filters={"name": ["in", list(user_ids)], "enabled": 1},
            fields=["name", "full_name", "user_image", "email"],
        )
        for u in user_data:
            if u.get("full_name"):
                parts = u["full_name"].split()
                u["abbr"] = "".join([p[0].upper() for p in parts if p])[:2]
            else:
                u["abbr"] = u["name"][0].upper() if u["name"] else "U"
        return user_data

    # Pre-fetch details for all known completing users
    completing_user_ids = [d["user"] for d in state_to_user.values()]
    all_past_users_data = get_user_details(list(set(completing_user_ids)))
    past_user_map = {u["name"]: u for u in all_past_users_data}

    def get_users_for_roles(roles, doc_owner):
        if not roles:
            return []

        users = set()
        for role in roles:
            if role == "All":
                users.add(doc_owner)
            else:
                role_users = frappe.get_all(
                    "Has Role", filters={"role": role}, pluck="parent"
                )
                users.update(role_users)

        # Filter out Administrator
        if "Administrator" in users:
            users.remove("Administrator")

        return get_user_details(list(users))

    # 3. Create Timeline Items
    journey_items = []

    # 3a. Identify Current state index
    current_index = (
        all_states_list.index(current_state) if current_state in all_states_list else -1
    )

    # Identify Current Roles for Current State Avatars
    current_roles = []
    if current_state:
        for transition in workflow.transitions:
            if transition.state == current_state and is_condition_satisfied(
                transition, doc
            ):
                if transition.allowed and transition.allowed not in current_roles:
                    current_roles.append(transition.allowed)

    # Resolve Current Users
    current_users = get_users_for_roles(current_roles, doc.owner)

    # 3b. Map States to Journey Items
    role_sets_seen = []
    if current_roles:
        role_sets_seen.append(", ".join(sorted(current_roles)))

    for i, state in enumerate(all_states_list):
        if i < current_index:
            # Past/Passed States - Only show if actually visited
            if state in state_to_user:
                log_data = state_to_user.get(state)
                completing_user = log_data.get("user")
                time_val = log_data.get("time")

                user_list = []
                if completing_user in past_user_map:
                    user_list = [past_user_map[completing_user]]

                journey_items.append(
                    {
                        "state": state,
                        "display_name": _(state),
                        "status": "past",
                        "icon": "solid-success",
                        "users": user_list,
                        "timestamp": frappe.utils.format_datetime(time_val)
                        if time_val
                        else None,
                        "index": i,
                    }
                )

        elif i == current_index:
            # Current State
            is_terminal = not any(t.state == state for t in workflow.transitions)
            status = "future" if is_terminal else "current"
            icon = "solid-success" if is_terminal else "solid-warning"

            journey_items.append(
                {
                    "state": state,
                    "display_name": _(state),
                    "status": status,
                    "icon": icon,
                    "users": current_users,
                    "timestamp": None,
                    "index": i,
                }
            )

        elif state in reachable_future_states:
            # Future States (only if reachable and not terminal)
            roles_for_this_state = []
            for transition in workflow.transitions:
                if transition.state == state and is_condition_satisfied(
                    transition, doc
                ):
                    if (
                        transition.allowed
                        and transition.allowed not in roles_for_this_state
                    ):
                        roles_for_this_state.append(transition.allowed)

            if roles_for_this_state:
                role_label = ", ".join(sorted(roles_for_this_state))
                if role_label not in role_sets_seen:
                    journey_items.append(
                        {
                            "state": state,
                            "display_name": _("Waiting Action"),
                            "status": "future",
                            "icon": "solid-info",
                            "users": [],
                            "index": i,
                        }
                    )
                    role_sets_seen.append(role_label)

    # 4. Final Sort by index and Render
    journey_items.sort(key=lambda x: x["index"])

    journey = []
    # Use a future time to pin the journey at the top, grouping items together
    base_time = frappe.utils.add_to_date(frappe.utils.now_datetime(), hours=2)
    total_items = len(journey_items)

    for i, item in enumerate(journey_items):
        # Frappe timeline is newest at top (desc).
        journey.append(
            {
                "icon": item["icon"],
                "icon_size": "sm",
                "is_card": True,
                "status": item["status"],
                "creation": frappe.utils.add_to_date(
                    base_time, seconds=(total_items - i)
                ),
                "template": "workflow_state_card",
                "template_data": {
                    "state": item["display_name"],
                    "status": item["status"],
                    "users": item.get("users", []),
                    "timestamp": item.get("timestamp"),
                },
            }
        )

    return journey


def get_workflow_actions_timeline_content(doctype, docname):
    """
    Returns simplified workflow state journey as timeline content.
    """
    workflow_name = frappe.db.get_value(
        "Workflow", {"document_type": doctype, "is_active": 1}, "name"
    )
    if not workflow_name:
        return []

    try:
        workflow = frappe.get_doc("Workflow", workflow_name)
        state_field = workflow.workflow_state_field
    except Exception:
        return []

    # Get State Journey
    timeline_items = get_state_journey(doctype, docname, state_field, workflow)

    return timeline_items
