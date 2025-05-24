from werkzeug.routing import Rule
from common.api.controllers.common.club import club_list, read_club

club_rules = [
	Rule("/hr-common/club", methods=["GET"], endpoint=club_list),
	Rule("/hr-common/club/<path:name>/", methods=["GET"], endpoint=read_club),
]