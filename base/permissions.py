import pyotp

from django.conf import settings
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class SwitchUserPermission(permissions.IsAuthenticated):
    """
    Permission class that allows users to switch to another user.
    """

    TOTP_SECRET = settings.TOTP_SECRET    

    def has_permission(self, request, view):
        """
        Check if the user has permission to switch to another user.

        Args:
            request (HttpRequest): The current request.
            view (View): The current view.

        Returns:
            bool: True if the user has permission, False otherwise.

        Raises:
            PermissionDenied: If the OTP is missing or invalid.
        """
        if request.method == "GET":
            return super().has_permission(request, view)

        # if settings.ENVIRONMENT == "local":
        #     return True
        
        if not self.TOTP_SECRET:
            raise PermissionDenied("Failed OTP.")
        
        current_otp = request.META.get("HTTP_OTP")
        if not current_otp:
            raise PermissionDenied("Can not find OTP in the request header.")
        
        totp = pyotp.TOTP(self.TOTP_SECRET)

        if totp.verify(current_otp, valid_window=1):
            return True
        raise PermissionDenied("Invalid OTP.")


class CombinedPermission(permissions.BasePermission):
    """This permission class checks the type of authentication token in the
    request and delegates permission checks to the appropriate permission class
    based on the token type.

    Methods:
        has_permission(request, view): Check if the user has permission to
            access the view.
        has_object_permission(request, view, obj): Check if the user has
            permission to perform the action on the object.
    """

    def has_permission(self, request, view):
        """Check if the user has permission to access the view.

        Args:
            request (HttpRequest): The HTTP request being checked for
                permission.
            view (View): The Django REST framework view being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        permission = self.permission(request)
        return permission.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Check if the user has permission to perform the action on the
        object.

        Args:
            request (HttpRequest): The HTTP request being checked for
                permission.
            view (View): The Django REST framework view being accessed.
            obj (object): The object being acted upon.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        permission = self.permission(request)
        return permission.has_object_permission(request, view, obj)

    def permission(self, request):
        """Get the appropriate permission class based on the authentication
        token type.

        Args:
            request (HttpRequest): The HTTP request being checked for
                permission.
        """

        if request.method == 'GET':
            return permissions.IsAuthenticated()
        
        if request.user and request.user.is_staff:
            token = request.auth
            if token.__class__._meta.label == 'oauth2_provider.AccessToken':
                from oauth2_provider.contrib.rest_framework import \
                    TokenMatchesOASRequirements
                return TokenMatchesOASRequirements()
        raise PermissionDenied("Invalid Access")