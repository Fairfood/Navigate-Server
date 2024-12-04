from oauth2_provider.exceptions import InvalidRequestFatalError
from oauth2_provider.oauth2_validators import AccessToken
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.scopes import get_scopes_backend
from oauthlib.oauth2.rfc6749 import utils


class OAuth2ClientAccessValidator(OAuth2Validator):
    """
    Custom OAuth 2.0 access token validator for client applications.

    This validator extends the default OAuth2Validator and provides additional
    functionality for creating access tokens.

    Attributes:
        None

    Methods:
        _create_access_token: Create and return an AccessToken instance.
    """

    def _create_access_token(
        self, expires, request, token, source_refresh_token=None
    ):
        """
        Create and return an AccessToken instance.

        Args:
            expires (datetime): The expiration datetime of the access token.
            request (oauthlib.common.Request): The request object.
            token (dict): The token data containing 'access_token', 'id_token',
                etc.
            source_refresh_token (oauth2_provider.models.RefreshToken, optional
            ):
                The refresh token from which the access token is generated.

        Returns:
            oauth2_provider.models.AccessToken: The created AccessToken
                instance.
        """

        id_token = token.get("id_token", None)
        if id_token:
            id_token = self._load_id_token(id_token)
        return AccessToken.objects.create(
            user=request.client.user,
            scope=token["scope"],
            expires=expires,
            token=token["access_token"],
            id_token=id_token,
            application=request.client,
            source_refresh_token=source_refresh_token,
        )
