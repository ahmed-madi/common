import frappe
from frappe import _


def get_user_info(user_id):
    """Helper to get user full name and image"""
    user_data = frappe.db.get_value(
        "User", user_id, ["full_name", "user_image"], as_dict=True
    )
    if not user_data:
        return {"name": user_id, "image": None}
    return {"name": user_data.full_name, "image": user_data.user_image}


def get_users_for_roles(roles):
    """Helper to get all users belonging to a list of roles"""
    if not roles:
        return []

    users = frappe.get_all(
        "Has Role",
        filters={"role": ["in", roles], "parenttype": "User"},
        pluck="parent",
    )

    unique_users = list(set(users))
    user_infos = []
    for user_id in unique_users:
        if user_id == "Administrator":
            continue
        user_infos.append(get_user_info(user_id))

    return user_infos
