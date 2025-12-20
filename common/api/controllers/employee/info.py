from frappe import _
from common.api.utils.resource import BaseResource
from common.api.utils.endpoints import document_list, update_doc, get_doc
from common.api.utils.decorators import safe_api
from werkzeug.routing import Rule


class MyEmployeeResource(BaseResource):
    doctype = "Employee"
    url_prefix = ""
    resource_name = "employee"
    fields = [
        "name",
        "status",
        "employee_name",
        "image",
        "gender",
        "date_of_birth",
        "designation",
        "department",
        "cell_number",
        "linkedin_profile_url",
        "personal_email",
        "company_email",
        "current_address",
    ]

    @classmethod
    def retrieve(cls):
        @safe_api
        def _retrieve(employee):
            doc = get_doc(
                cls.doctype,
                employee,
                add_perms=False,
                add_wf=False,
                ignore_perms=False,
                fields=cls.fields,
            )
            msg = _("{} data fetched").format(_(cls.doctype))
            return doc, msg

        _retrieve.__name__ = "employee_info"
        return _retrieve

    @classmethod
    def update(cls):
        @safe_api
        def _update(employee):
            only_for = [
                "cell_number",
                "personal_email",
                "current_address",
                "linkedin_profile_url",
            ]
            return update_doc(
                cls.doctype, employee, only_for=only_for, ignore_perms=True
            )

        _update.__name__ = "update_employee_info"
        return _update

    @classmethod
    def get_routes(cls):
        return [
            Rule(
                "/employee/<path:employee>/", methods=["GET"], endpoint=cls.retrieve()
            ),
            Rule("/employee/<path:employee>/", methods=["PUT"], endpoint=cls.update()),
        ]


class OtherEmployeeInfoResource(BaseResource):
    doctype = "Employee"
    url_prefix = ""
    resource_name = "employee-info"
    fields = [
        "name",
        "status",
        "employee_name",
        "image",
        "gender",
        "date_of_birth",
        "designation",
        "department",
        "cell_number",
        "linkedin_profile_url",
        "personal_email",
        "company_email",
        "current_address",
    ]
    list_fields = [
        "name",
        "status",
        "employee_name",
        "image",
        "designation",
        "department",
    ]

    @classmethod
    def list(cls):
        @safe_api
        def _list():
            return document_list(
                cls.doctype,
                cls.list_fields,
                ignore_perms=True,
                add_perms=False,
                add_wf=False,
                user_filters=[["status", "=", "Active"]],
                force_user_filters=True,
            )

        _list.__name__ = "other_employee_info_list"
        return _list

    @classmethod
    def retrieve(cls):
        @safe_api
        def _retrieve(employee):
            doc = get_doc(
                cls.doctype,
                employee,
                add_perms=False,
                add_wf=False,
                ignore_perms=True,
                fields=cls.fields,
            )
            msg = _("{} data fetched").format(_(cls.doctype))
            return doc, msg

        _retrieve.__name__ = "other_employee_info"
        return _retrieve

    @classmethod
    def get_routes(cls):
        return [
            Rule(
                "/employee-info/",
                methods=["GET"],
                endpoint=cls.list(),
            ),
            Rule(
                "/employee-info/<path:employee>/",
                methods=["GET"],
                endpoint=cls.retrieve(),
            ),
        ]
