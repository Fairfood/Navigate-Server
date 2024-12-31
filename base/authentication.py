"""Module to override the default authentication."""
import os
import jwt
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, 
    get_authorization_header
)
from importlib import import_module
from sentry_sdk import set_tag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.oauth2_backends import get_oauthlib_core

from base import session


class JWTAuthentication(BaseAuthentication):
    """
    JWT Authentication class for Django REST Framework.

    This class provides authentication using JSON Web Tokens (JWT) for Django 
    REST Framework. It verifies the JWT token provided in the request's 
    authorization header and authenticates the user based on the token.

    Attributes:
        keyword (str): The keyword used in the authorization header to specify 
            the token type.
        verification_key_file (str): The file name of the public key used for 
            token verification.
        request (HttpRequest): The current request object.

    Methods:
        authenticate(request): Authenticates the user based on the JWT token in 
            the request's authorization header.
        validate_authorization_header(auth): Validates the authorization header 
            and extracts the token.
        authenticate_credentials(key): Authenticates the user based on the 
            token.
        get_auth_user(token): Retrieves the authenticated user based on the 
            token.
        get_user_nodes(user, token): Retrieves the nodes associated with the 
            authenticated user.
        verify_token(token): Verifies the JWT token using the public key.
        load_public_key_pem(path): Loads a public key from a PEM file.

    Raises:
        AuthenticationFailed: If the authorization header is invalid or the 
            token is expired/invalid.
    """
    
    keyword = 'Bearer'
    verification_key_file = os.path.join(settings.BASE_DIR, "public-key.pem")
    request = None

    def authenticate(self, request):
        """
        Authenticates the request based on the provided authorization header.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            User: The authenticated user if the authorization header is valid, 
            None otherwise.
        """
        self.request = request
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        token = self.validate_authorization_header(auth)
        return self.authenticate_credentials(token)

    def validate_authorization_header(self, auth):
        """
        Validates the authorization header.

        Args:
            auth (list): The authorization header as a list of strings.

        Returns:
            str: The token extracted from the authorization header.

        Raises:
            AuthenticationFailed: If the authorization header is invalid.
        """
        if len(auth) == 1:
            msg = _('Invalid token header. '
                    'No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        
        elif len(auth) > 2:
            msg = _('Invalid token header. '
                    'Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
            return token
        except UnicodeError:
            msg = _('Invalid token header. '
                    'Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

    def authenticate_credentials(self, key):
        """
        Authenticates the user's credentials based on the provided key.

        Args:
            key (str): The authentication key.

        Returns:
            tuple: A tuple containing the authenticated user and the key.

        """
        token = self.verify_token(key)
        user = self.get_auth_user(token)
        user_nodes = self.get_user_nodes(user, token)
        self.request.session['nodes'] = user_nodes
        self.request.session['user_type'] = token.get('user_type')
        self.request.session['email_verified'] = token.get('email_verified')
        
        self.set_session(user)
        
        return (user, key)

    def get_auth_user(self, token):
        """
        Retrieves the authenticated user based on the provided token.

        Args:
            token (dict): The token containing user information.

        Returns:
            User: The authenticated user.

        Raises:
            AuthenticationFailed: If the user cannot be identified.
        """
        UserModel = get_user_model()
        try:
            user_id = token["sub"]
            user_email = token["email"]
            user = UserModel.objects.get(
                sso_id=user_id, email=user_email
            )
        except (UserModel.DoesNotExist, KeyError):
            msg = _("Unable to identify user")
            raise exceptions.AuthenticationFailed(msg)
        return user

    def get_user_nodes(self, user, token):
        """
        Retrieves the available nodes for a given user based on the provided 
        token.

        Args:
            user (User): The user for whom to retrieve the available nodes.
            token (dict): The token containing the nodes information.

        Returns:
            QuerySet: A queryset of available nodes for the user.

        """
        token_nodes = token.get('nodes', {})
        avaliable_nodes = user.companies.filter(sso_id__in=token_nodes.keys())
        return [node.pk.hashid for node in avaliable_nodes]

    def verify_token(self, token):
        """
        Verifies the authenticity of a token.

        Args:
            token (str): The token to be verified.

        Returns:
            dict: The decoded token if it is valid.

        Raises:
            AuthenticationFailed: If the token has expired or is invalid.
        """
        secret_key = self.load_public_key_pem(self.verification_key_file)
        audience = settings.TRACE_OAUTH2_CLIENT_ID
        try:
            decoded_token = jwt.decode(
                token, secret_key, 
                algorithms=["RS256"],
                audience=audience
                )
            return decoded_token
        except jwt.ExpiredSignatureError:
            msg = _("Token has expired.")
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            msg = _("Invalid token or signature.")
            raise exceptions.AuthenticationFailed(msg)

    @staticmethod
    def load_public_key_pem(path):
        """
        Load a public key from a PEM file.

        Args:
            path (str): The path to the PEM file.

        Returns:
            str: The public key in PEM format.

        Raises:
            FileNotFoundError: If the specified file path does not exist.
            ValueError: If the specified file is not a valid PEM file.
            cryptography.exceptions.UnsupportedAlgorithm: If the key file uses 
                an unsupported algorithm.
        """
        with open(path, 'rb') as key_file:
            key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def set_session(self, user):
        """Sets the user and company IDs to the session."""
        session.set_to_local("user_id", user.pk.hashid)

        entity_id = self.request.headers.get('Entity-ID')
        if not entity_id:
            session.set_to_local(
                "company_id", self.request.session.get("nodes")[0])
        if entity_id not in self.request.session.get("nodes"):
            raise exceptions.AuthenticationFailed(
                f"Invalid Entity ID: {entity_id}"
            )
        session.set_to_local("company_id", entity_id)

        

class SwitchJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class that switches to JWT authentication only for 
    GET requests.

    Inherits from JWTAuthentication class.
    """

    def authenticate(self, request):
        """
        Authenticates the request.

        Overrides the authenticate method of the parent class.
        Returns the authenticated user if the request method is 'GET', 
        otherwise returns None.
        """
        if request.method == 'GET':
            return super().authenticate(request)
        return None


class AuthMixin:

    def set_section(self, user, validated_token):
        """Set session data to local storage and tags based on the
        authentication method used.

        Args:
            user (User): The authenticated user.
            validated_token (dict): Validated token data.
        """

        session_data = {}
        if self.__class__.__name__ == "CustomOAuth2Authentication":
            session_data = {
                "user_id": user.id,
            }

        # Set session data to local storage and tags
        for k, v in session_data.items():
            session.set_to_local(k, v)
            set_tag(f"session.{k}", v)


class CustomOAuth2Authentication(OAuth2Authentication, AuthMixin):
    """Custom OAuth2 authentication class with extended functionality.

    This class extends the default OAuth2Authentication to provide
    additional features.
    """

    def authenticate(self, request):
        """Returns two-tuple of (user, token) if authentication succeeds, or
        None otherwise."""
        oauthlib_core = get_oauthlib_core()

        # Adding default scope for
        valid, r = oauthlib_core.verify_request(
            request, scopes=[]
        )
        if valid:
            self.set_section(r.user, r.access_token)
            return r.user, r.access_token
        request.oauth2_error = getattr(r, "oauth2_error", {})
        return None


class CustomDynamicAuthentication(BaseAuthentication):
    """
    Custom authentication class that dynamically selects and uses the appropriate
    authentication mechanism based on the `Auth-Type` header in the request.
    """

    def get_auth_class(self, auth_type):
        """
        Retrieves the authentication class based on the provided auth type.

        Args:
            auth_type (str): The type of authentication specified in the request header.

        Returns:
            Type: The authentication class corresponding to the auth type.

        Raises:
            AuthenticationFailed: If the provided auth type is not supported.
        """

        # Get the authentication class path from settings
        auth_class_path = settings.AUTH_TYPE_CLASSES.get(auth_type)
        if not auth_class_path:
            raise exceptions.AuthenticationFailed(
                f"Unsupported authentication type: {auth_type}"
            )
        # Split the path into module path and class name
        module_path, class_name = auth_class_path.rsplit(".", 1)

        # Import the module and get the class
        module = import_module(module_path)
        return getattr(module, class_name)

    def authenticate(self, request):
        """
        Dynamically selects and uses the appropriate authentication mechanism based on the
        `Auth-Type` header in the request. Calls the `authenticate` method of the selected
        authentication class.

        Args:
            request (HttpRequest): The HTTP request object containing the authentication data.

        Returns:
            tuple or None: A tuple of (user, auth) if authentication is successful, or None if not.
        """

        # Extract auth type from request header or default to 'password_grant'
        auth_type = request.headers.get("Auth-Type", "external_auth").lower()

        # Get the relevant authentication class
        auth_class = self.get_auth_class(auth_type)
        # Instantiate the authentication class and authenticate
        return auth_class().authenticate(request)