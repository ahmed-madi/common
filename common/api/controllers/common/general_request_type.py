from common.api.utils.resource import BaseResource


class GeneralRequestTypeResource(BaseResource):
    doctype = "General Request Type"
    fields = ["name", "request_type"]
