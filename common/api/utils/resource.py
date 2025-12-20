from werkzeug.routing import Rule
from common.api.utils.decorators import safe_api
from common.api.utils.endpoints import (
    document_list,
    read_doc,
    create_doc,
    update_doc,
    delete_doc,
)


class BaseResource:
    """
    Base class for API resources.
    Encapsulates standard CRUD logic and route generation.
    """

    doctype = None
    fields = ["*"]

    # URL Configuration
    url_prefix = "/hr-common"
    resource_name = None  # Auto-generated from doctype if not set

    # Permissions & Workflow Configuration
    add_perms = False
    add_wf = False
    ignore_perms = False

    # List Specific Params
    list_user_filters = []
    list_force_user_filters = False

    @classmethod
    def get_list_filters(cls):
        """Override this to return dynamic filters"""
        return cls.list_user_filters

    @classmethod
    def list(cls):
        """Standard List Endpoint"""

        @safe_api
        def _list():
            return document_list(
                cls.doctype,
                cls.fields,
                add_perms=cls.add_perms,
                add_wf=cls.add_wf,
                user_filters=cls.get_list_filters(),
                force_user_filters=cls.list_force_user_filters,
            )

        _list.__name__ = f"{cls.doctype.replace(' ', '_').lower()}_list"
        return _list

    @classmethod
    def create(cls):
        """Standard Create Endpoint"""

        @safe_api
        def _create():
            return create_doc(cls.doctype, add_perms=cls.add_perms, add_wf=cls.add_wf)

        _create.__name__ = f"{cls.doctype.replace(' ', '_').lower()}_create"
        return _create

    @classmethod
    def retrieve(cls):
        """Standard Retrieve Endpoint"""

        @safe_api
        def _retrieve(name):
            return read_doc(
                cls.doctype,
                name,
                fields=cls.fields,
                add_perms=cls.add_perms,
                add_wf=cls.add_wf,
                ignore_perms=cls.ignore_perms,
            )

        _retrieve.__name__ = f"{cls.doctype.replace(' ', '_').lower()}_retrieve"
        return _retrieve

    @classmethod
    def update(cls):
        """Standard Update Endpoint"""

        @safe_api
        def _update(name):
            return update_doc(
                cls.doctype,
                name,
                add_perms=cls.add_perms,
                add_wf=cls.add_wf,
                ignore_perms=cls.ignore_perms,
            )

        _update.__name__ = f"{cls.doctype.replace(' ', '_').lower()}_update"
        return _update

    @classmethod
    def delete(cls):
        """Standard Delete Endpoint"""

        @safe_api
        def _delete(name):
            return delete_doc(cls.doctype, name)

        _delete.__name__ = f"{cls.doctype.replace(' ', '_').lower()}_delete"
        return _delete

    @classmethod
    def get_routes(cls):
        """
        Generate Werkzeug Rules for this resource.
        Override this or add methods to allow custom actions.
        """
        if not cls.doctype:
            raise ValueError("doctype must be set on Resource class")

        name = cls.resource_name or cls.doctype.lower().replace(" ", "-")
        base_url = f"{cls.url_prefix}/{name}"

        routes = [
            Rule(base_url, methods=["GET"], endpoint=cls.list()),
            Rule(base_url, methods=["POST"], endpoint=cls.create()),
            Rule(f"{base_url}/<path:name>/", methods=["GET"], endpoint=cls.retrieve()),
            Rule(f"{base_url}/<path:name>/", methods=["PUT"], endpoint=cls.update()),
            Rule(f"{base_url}/<path:name>/", methods=["DELETE"], endpoint=cls.delete()),
        ]

        # Auto-discover custom actions?
        # For now, let's keep it simple. Subclasses can append to this list.

        return routes


class SingletonResource(BaseResource):
    """
    Resource for Single DocTypes.
    Only exposes GET /resource which returns the single document.
    """

    @classmethod
    def get_routes(cls):
        if not cls.doctype:
            raise ValueError("doctype must be set on Resource class")

        name = cls.resource_name or cls.doctype.lower().replace(" ", "-")
        base_url = f"{cls.url_prefix}/{name}"

        # Override retrieve to fetch the singleton (name=doctype)
        @safe_api
        def _get_singleton():
            return read_doc(
                cls.doctype,
                cls.doctype,
                add_perms=cls.add_perms,
                add_wf=cls.add_wf,
                fields=cls.fields if cls.fields != ["*"] else [],  # Handle fields
            )

        return [Rule(base_url, methods=["GET"], endpoint=_get_singleton)]
