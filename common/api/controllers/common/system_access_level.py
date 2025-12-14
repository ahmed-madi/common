from common.api.utils.resource import BaseResource

class SystemAccessLevelResource(BaseResource):
    doctype = "System Access Level"
    fields = ["name", "access_level"]
