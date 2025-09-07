from werkzeug.routing import Rule
from common.api.controllers.common.language import language_list, read_language

language_rules = [
    Rule("/hr-common/language", methods=["GET"], endpoint=language_list),
    Rule("/hr-common/language/<path:name>/", methods=["GET"], endpoint=read_language),
]
