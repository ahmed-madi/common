from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "product_name", "is_term_loan", "disabled"]


def loan_product_list():
    doctype = "Loan Product"
    return document_list(doctype, fields, translate_text=True, tr_field="product_name")


def read_loan_product(name: str):
    doctype = "Loan Product"
    return read_doc(doctype, name, origin_fields=fields)
