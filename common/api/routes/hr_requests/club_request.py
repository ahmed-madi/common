from werkzeug.routing import Rule
from common.api.controllers.hr_requests.club_request import club_list, create_club, read_club, update_club, delete_club

club_request_rules = [
	Rule("/hr-requests/club-request", methods=["GET"], endpoint=club_list),
	Rule("/hr-requests/club-request", methods=["POST"], endpoint=create_club),
	Rule("/hr-requests/club-request/<path:name>/", methods=["GET"], endpoint=read_club),
	Rule("/hr-requests/club-request/<path:name>/", methods=["PUT"], endpoint=update_club),
	Rule("/hr-requests/club-request/<path:name>/", methods=["DELETE"], endpoint=delete_club),
]