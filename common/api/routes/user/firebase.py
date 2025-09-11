from werkzeug.routing import Rule
from common.api.utils.endpoints import handle_call


def get_config():
    return handle_call("common.api.controllers.user.firebase.get_config")


def subscribe():
    return handle_call("common.api.controllers.user.firebase.subscribe")


def unsubscribe():
    return handle_call("common.api.controllers.user.firebase.unsubscribe")


def update_user_settings():
    return handle_call(
        "common.api.controllers.user.firebase.update_user_settings"
    )

def get_user_settings():
    return handle_call(
        "common.api.controllers.user.firebase.get_user_settings"
    )


firebase_rules = [
    Rule("/user/fcm-configs", methods=["GET"], endpoint=get_config),
    Rule("/user/fcm-subscribe", methods=["POST"], endpoint=subscribe),
    Rule("/user/fcm-unsubscribe", methods=["DELETE"], endpoint=unsubscribe),
    Rule(
        "/user/user-settings",
        methods=["GET"],
        endpoint=get_user_settings,
    ),
    Rule(
        "/user/user-settings",
        methods=["POST"],
        endpoint=update_user_settings,
    ),
]
