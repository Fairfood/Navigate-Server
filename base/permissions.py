import pyotp

from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class SwitchUserPermission(IsAuthenticated):
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
