from common.api.utils.resource import BaseResource
from common.api.utils.endpoints import read_doc
from common.api.utils.decorators import safe_api
from werkzeug.routing import Rule

class SalarySlipResource(BaseResource):
    doctype = "Salary Slip"
    
    @classmethod
    def download_slip(cls):
        @safe_api
        def _download(employee, name):
            # Verify employee exists (as per original logic)
            read_doc("Employee", employee, fields=["name"])
            # Verify salary slip exists
            read_doc("Salary Slip", name, fields=["name"])
            
            from frappe.utils.print_format import download_pdf
            return download_pdf(doctype="Salary Slip", name=name)
        
        _download.__name__ = "download_salary_slip"
        return _download

    @classmethod
    def get_routes(cls):
        return [
            Rule(
                "/employee/<path:employee>/download-slip/<path:name>",
                methods=["GET"],
                endpoint=cls.download_slip(),
            )
        ]
