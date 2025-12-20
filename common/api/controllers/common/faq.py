from common.api.utils.resource import BaseResource


class FAQResource(BaseResource):
    doctype = "FAQ"
    fields = ["name", "question", "answer"]
