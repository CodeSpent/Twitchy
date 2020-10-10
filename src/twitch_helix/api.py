import requests
import json
from typing import Union
import datetime


class API(object):
    """Represents a connection to Twitch's Helix API.

    Attributes:
        client_id (str): Twitch Client ID.
        client_secret (str): Twitch Client Secret.
        oauth_token (str, optional): User oauth token for requests needing oauth.

    """

    def __init__(
        self, client_id: str = None, client_secret: str = None, oauth_token: str = None
    ):

        if client_id is None or client_secret is None and oauth_token is None:
            raise TypeError(
                "You must provide both 'client_id' and 'client_secret' args or a valid oauth token."
            )

        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.oauth_token: str = oauth_token
        self.refresh_token: str = None
        self.scope: str = None
        self.token_expiration: datetime.datetime = None

        # all base urls should exclude trailing slash
        self._base_url: str = "https://api.twitch.tv/helix"
        self._auth_url: str = "https://id.twitch.tv/oauth2/token"
        self._token_validation_url: str = "https://id.twitch.tv/oauth2/validate"
        self._webhooks_hub_url: str = "https://api.twitch.tv/helix/webhooks/hub"
        self._headers: dict = {}

        self._authenticate()

    def _set_headers(self, headers: dict) -> None:
        self._headers.update(headers)
        self._headers["Client-id"] = self.client_id

        if self.oauth_token is not None:
            self._headers["Authorization"] = " ".join(["Bearer", self.oauth_token])

    def _request(
        self,
        endpoint: str = None,
        url: str = None,
        method="get",
        params={},
        data={},
        headers={},
    ) -> dict:
        self._set_headers(headers)

        if url is None and endpoint is not None:
            url = "/".join([self._base_url, endpoint])

        response = requests.request(
            method, url, params=params, data=data, headers=self._headers
        )

        if response.ok:
            data = response.json()
            try:
                data = response.json()
            except ValueError:
                data = json.loads({})
            return data
        else:
            response.raise_for_status()

    def _authenticate(self) -> bool:
        tokens = self._get_oauth_tokens(self.client_id, self.client_secret)

        # oauth_token needs to be set before validation in order
        # for the authorization header to get set in _set_headers()
        # invalidate the token if validation fails
        self.oauth_token = tokens["access_token"]
        validated_tokens = self._validate_token(tokens["access_token"])

        try:
            if validated_tokens["client_id"] == self.client_id:
                self.oauth_token = tokens["access_token"]
                self.refresh_token = tokens["refresh_token"]
                self.scope = tokens["scope"]
                self._set_token_expiration(tokens["expires_in"])
                return True
            else:
                self.oauth_token = None
                return False
        except KeyError:
            self.oauth_token = None
            return False

    def _get_oauth_tokens(self, client_id: str, client_secret: str) -> dict:
        if self.oauth_token is not None:
            return self.oauth_token

        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }

        data = self._request(url=self._auth_url, method="post", data=payload)

        if "access_token" in data:
            return data

    def _validate_token(self, token: str) -> dict:
        return self._request(url=self._token_validation_url)

    def _set_token_expiration(self, token_expires_in: int) -> None:
        self.token_expiration = (
            datetime.datetime.now() + datetime.timedelta(seconds=token_expires_in)
        ) - datetime.timedelta(minutes=5)

    def get_users(
        self, user_id: Union[str, list] = None, login: Union[str, list] = None
    ) -> list:
        params = {}
        if user_id is not None:
            params["id"] = user_id
        elif login is not None:
            params["login"] = login
        else:
            raise ValueError("'user_id' or 'user_login' argument required.")

        data = self._request("users", params=params)
        return data["data"]
