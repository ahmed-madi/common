from werkzeug.routing import Rule
from common.api.utils.endpoints import handle_call

def get_config():
    return handle_call("common.api.controllers.user.firebase.get_config")

def subscribe():
    return handle_call("common.api.controllers.user.firebase.subscribe")

def unsubscribe():
    return handle_call("common.api.controllers.user.firebase.unsubscribe")


firebase_rules = [
	Rule("/user/fcm-configs", methods=["GET"], endpoint=get_config),
	Rule("/user/fcm-subscribe", methods=["POST"], endpoint=subscribe),
	Rule("/user/fcm-unsubscribe", methods=["DELETE"], endpoint=unsubscribe),
]