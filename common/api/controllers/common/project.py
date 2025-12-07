from common.api.utils.resource import BaseResource

class ProjectResource(BaseResource):
    doctype = "Project"
    fields = ["name", "project_name", "priority", "status", "is_active"]
