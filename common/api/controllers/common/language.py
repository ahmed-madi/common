from common.api.utils.resource import BaseResource

class LanguageResource(BaseResource):
    doctype = "Language"
    fields = ["name", "language_name", "language_code", "flag", "based_on"]
    
    list_user_filters = [["enabled", "=", 1]]
    list_force_user_filters = True
