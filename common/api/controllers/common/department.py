from common.api.utils.endpoints import document_list, read_doc

fields = ["name", "department_name", "disabled", "is_group"]
doctype = "Department"


def department_list():
    return document_list(
        doctype,
        fields,
        user_filters=[["disabled", "=", 0]],
        force_user_filters=True,
        add_perms=False,
        add_wf=False,
    )


def read_department(name: str):
    return read_doc(
        doctype,
        name,
        add_perms=False,
        add_wf=False,
        fields=fields,
    )
