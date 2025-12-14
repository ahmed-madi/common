from common.api.utils.resource import BaseResource

class SalaryFixationReasonResource(BaseResource):
    doctype = "Fixation Reason"
    resource_name = "salary-fixation-reason"
    fields = ["name", "fixation_reason"]
