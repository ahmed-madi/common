from common.api.utils.resource import BaseResource


class CompanyNewsletterResource(BaseResource):
    doctype = "Company Newsletter"
    url_prefix = "/company"
    resource_name = "newsletter"
    fields = [
        "name",
        "subject",
        "publish_on",
        "cover_image",
        "published",
        "intro_description",
        "list_image",
    ]
    list_user_filters = [["published", "=", "1"]]
    list_force_user_filters = True
