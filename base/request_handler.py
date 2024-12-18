from typing import Any

from rest_framework import viewsets


class OAuthScopeViewSetMixin:
    """Mixin class for providing OAuth scope information for a Django REST
    framework viewset.

    Attributes:
        resource_types (list): List of resource types associated with the
                               viewset.

    Methods:
        get_required_alternate_scopes(): Get required alternate OAuth scopes
            based on HTTP methods and resource types.
    """

    resource_types = []

    def get_required_alternate_scopes(self):
        """Get the required alternate OAuth scopes based on HTTP methods and
        resource types.

        Returns:
            dict: A dictionary mapping HTTP methods to lists of alternate OAuth
                scopes.
        """
        required_scopes = {}
        method_scopes_mapping = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }

        for method in self.http_method_names:
            upper_method = method.upper()
            if upper_method in method_scopes_mapping:
                required_scopes[upper_method] = [
                    [
                        f"{method_scopes_mapping[upper_method]}:"
                        f"{resource_type}"
                        for resource_type in self.resource_types
                    ]
                ]
        return required_scopes


class CustomScopeViewset(OAuthScopeViewSetMixin, viewsets.ModelViewSet):
    """Viewset combining OAuth scope information, and Django REST
    framework's ModelViewSet.

    This viewset inherits from `OAuthScopeViewSetMixin` for providing 
    OAuth scope information, and `viewsets.ModelViewSet` for typical 
    model viewset functionality.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.required_alternate_scopes = self.get_required_alternate_scopes()
