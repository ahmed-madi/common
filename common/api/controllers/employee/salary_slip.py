from common.api.utils.endpoints import (
    read_doc,
)


def download_salary_slip(employee: str, name: str):
    read_doc("Employee", employee, fields=["name"])
    read_doc("Salary Slip", name, fields=["name"])
    from frappe.utils.print_format import download_pdf
    
    return download_pdf(doctype="Salary Slip", name=name)
