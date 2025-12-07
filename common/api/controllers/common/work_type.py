from common.api.utils.resource import BaseResource

class WorkTypeResource(BaseResource):
    doctype = "Work Type"
    fields = ["name", "type"]
