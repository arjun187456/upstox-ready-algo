"""Upstox OAuth2 authentication helper."""

import upstox_client
from upstox_client.rest import ApiException

from .config import Config


class UpstoxAuth:
    """Handles Upstox API authentication.

    Usage
    -----
    Either set ``UPSTOX_ACCESS_TOKEN`` in your environment/.env file for a
    pre-obtained token, or call :meth:`get_authorization_url` / :meth:`exchange_code`
    to go through the OAuth2 flow interactively.
    """

    def __init__(self) -> None:
        self._configuration = upstox_client.Configuration()
        self._configuration.access_token = Config.ACCESS_TOKEN

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def configuration(self) -> upstox_client.Configuration:
        """Return the current SDK configuration object."""
        return self._configuration

    # ------------------------------------------------------------------
    # OAuth2 helpers
    # ------------------------------------------------------------------

    def get_authorization_url(self) -> str:
        """Build the Upstox OAuth2 authorization URL.

        The user must visit this URL, log in, and grant access.  Upstox will
        redirect to ``REDIRECT_URI`` with a ``code`` query-parameter.
        """
        return (
            "https://api.upstox.com/v2/login/authorization/dialog"
            f"?response_type=code"
            f"&client_id={Config.API_KEY}"
            f"&redirect_uri={Config.REDIRECT_URI}"
        )

    def exchange_code(self, code: str) -> str:
        """Exchange an authorisation *code* for an access token.

        Parameters
        ----------
        code:
            The ``code`` value from Upstox's redirect.

        Returns
        -------
        str
            The access token string; also stored on this instance for
            subsequent API calls.
        """
        api_client = upstox_client.ApiClient(self._configuration)
        login_api = upstox_client.LoginApi(api_client)
        try:
            response = login_api.token(
                upstox_client.TokenRequest(
                    code=code,
                    client_id=Config.API_KEY,
                    client_secret=Config.API_SECRET,
                    redirect_uri=Config.REDIRECT_URI,
                    grant_type="authorization_code",
                )
            )
            access_token: str = response.data.access_token
            self._configuration.access_token = access_token
            return access_token
        except ApiException as exc:
            raise RuntimeError(f"Token exchange failed: {exc}") from exc

    def set_access_token(self, token: str) -> None:
        """Directly set a pre-obtained access token."""
        self._configuration.access_token = token
