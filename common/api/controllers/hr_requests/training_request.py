from common.api.utils.resource import BaseResource


class TrainingRequestResource(BaseResource):
    doctype = "Training Request"
    url_prefix = "/hr-requests"
    resource_name = "training-request"
    fields = [
        "name",
        "employee",
        "employee_name",
        "training_title",
        "request_date",
        "start_date",
        "end_date",
        "is_paid",
        "status",
    ]
    add_perms = True
    add_wf = True
