from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "product_name", "is_term_loan"]
doctype = "Loan Product"


def loan_product_list():
    return document_list(
        doctype,
        fields,
        user_filters=[["disabled", "=", 0]],
        force_user_filters=True,
        add_perms=False,
        add_wf=False,
    )


def read_loan_product(name: str):
    return read_doc(doctype, name, add_perms=False, add_wf=False, fields=fields)
