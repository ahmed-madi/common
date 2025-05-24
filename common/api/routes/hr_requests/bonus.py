from werkzeug.routing import Rule
from common.api.controllers.hr_requests.bonus import bonus_list, create_bonus, read_bonus, update_bonus, delete_bonus

bonus_rules = [
	Rule("/hr-requests/bonus", methods=["GET"], endpoint=bonus_list),
	Rule("/hr-requests/bonus", methods=["POST"], endpoint=create_bonus),
	Rule("/hr-requests/bonus/<path:name>/", methods=["GET"], endpoint=read_bonus),
	Rule("/hr-requests/bonus/<path:name>/", methods=["PUT"], endpoint=update_bonus),
	Rule("/hr-requests/bonus/<path:name>/", methods=["DELETE"], endpoint=delete_bonus),
]