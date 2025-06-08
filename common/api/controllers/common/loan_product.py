from common.api.utils.endpoints import document_list, read_doc

def loan_product_list():
    doctype = "Loan Product"
    fields = ["name", "product_name", "is_term_loan", "disabled"]
    return document_list(doctype, fields)

def read_loan_product(name: str):
    doctype = "Loan Product"
    fields = ["name", "product_name", "is_term_loan", "disabled"]
    return read_doc(doctype, name, origin_fields=fields)
