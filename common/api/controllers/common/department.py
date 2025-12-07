from common.api.utils.resource import BaseResource

class DepartmentResource(BaseResource):
    doctype = "Department"
    fields = ["name", "department_name", "disabled", "is_group"]
    
    list_user_filters = [["disabled", "=", 0]]
    list_force_user_filters = True
    
    # Legacy function exports for backward compatibility if needed, 
    # but for route file refactor we will use the class directly.
    # We don't need to export functions anymore.
