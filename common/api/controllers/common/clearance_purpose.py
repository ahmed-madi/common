from common.api.utils.resource import BaseResource

class ClearancePurposeResource(BaseResource):
    doctype = "Clearance Letter Purpose"
    resource_name = "clearance-purpose"
    fields = ["name", "purpose"]
