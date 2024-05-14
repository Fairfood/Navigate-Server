
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.utils import timezone

from base.models import AbstractBaseModel


class CustomUserManager(UserManager):
    """
    Custom manager for the User model.
    """
    def format_username(self, email: str) -> str:
        """Returns a formatted username based on the email address."""
        return email.split('@')[0] + str(timezone.now().timestamp())
    
    def create_user(self, username=None, email=None, password=None, 
                    **extra_fields):
        """
        Creates a new user with the given username, email, and password.

        Args:
            username (str, optional): The username for the new user. 
            If not provided, it will be derived from the email.
            email (str, optional): The email address for the new user.
            password (str, optional): The password for the new user.
            **extra_fields: Additional fields to be passed to the underlying 
            `create_user` method.

        Returns:
            User: The newly created user object.

        """
        if not username:
            username = self.format_username(email)
        return super().create_user(username, email, password, **extra_fields)
    
    def create_superuser(
            self, username=None, email=None, password=None, **extra_fields
            ):
        """
        Creates a new superuser with the given username, email, and password.

        Args:
            username (str, optional): The username for the new superuser. 
            If not provided, it will be derived from the email.
            email (str, optional): The email address for the new superuser.
            password (str, optional): The password for the new superuser.
            **extra_fields: Additional fields to be passed to the underlying 
            `create_superuser` method.
        """
        if not username:
            username = self.format_username(email)
        return super().create_superuser(
            username, email, password, **extra_fields)
    

class User(AbstractBaseModel, AbstractUser):
    """
    Represents a user in the system.

    Inherits from the Django's AbstractUser class and adds additional fields 
    and methods specific to our application.

    Attributes:
        email (str): The email address of the user.
        profile_image (ImageField): The profile image of the user.
        email_verified (bool): A flag indicating whether the user's email

        objects (CustomUserManager): The custom manager for the User model.
    """
    email = models.EmailField(
        _("email address"), 
        unique=True, 
        error_messages={
            "unique": _("A user with that email already exists."),
        }
    )
    profile_image = models.ImageField(
        _("profile image"), 
        upload_to="profile_images/", 
        null=True, blank=True
    )
    email_verified = models.BooleanField(default=False)

    objects = CustomUserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return f'{self.get_full_name()}({self.username})'
    
    def save(self, *args, **kwargs):
        """
        Save the user model instance.

        This method is responsible for saving the user model instance to the 
        database. If the `username` attribute is not set, it generates a new 
        username using the `format_username` method.

        """
        if not self.username:
            self.username = self._meta.get_field(self.USERNAME_FIELD
                                                 ).value_from_object(self)
        return super().save(*args, **kwargs)