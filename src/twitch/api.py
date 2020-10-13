import requests
import json
from typing import Union
import datetime

from .utils import get_scope_list_from_string
from .resources import TwitchObject, User, Cheermote
from .base import API


class Helix(object):
    """Represents a connection to Twitch's Helix API.

    Attributes:
        client_id (str): Twitch Client ID.
        client_secret (str): Twitch Client Secret.
        oauth_token (str, optional): User oauth token.

    """

    def __init__(
        self, client_id: str = None, client_secret: str = None, oauth_token: str = None
    ):

        if (client_id is None or client_secret is None) and oauth_token is None:
            raise TypeError(
                "You must provide both 'client_id' and 'client_secret' args or a valid oauth token."
            )

        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.oauth_token: str = oauth_token
        self.refresh_token: str = None
        self.scopes: list = None

    def get_users(
        self, user_id: Union[str, list] = None, login: Union[str, list] = None
    ) -> list:
        """Gets information about one or more specified Twitch users.

        Note:
            If authenticating as a user, provide no args to get authenticated user.

        Args:
            user_id (str, list, optional): User ID. Multiple user ids can be provided as a list. Limit: 100.
            login (str, list, optional): User login name. Multiple login names can be provided as a list. Limit: 100.

        Returns:
            list: List containing User objects.

        """

        params = {}

        if user_id is not None:
            params["id"] = user_id
        if login is not None:
            params["login"] = login

        if user_id is None and login is None and self.oauth_token is not None:
            validated_tokens = API(
                client_id=self.client_id,
                client_secret=self.client_secret,
                oauth_token=self.oauth_token,
                resource=User,
                path=None,
            )._get_validated_tokens()

            if "login" in validated_tokens:
                self.get_users(login=validated_tokens["login"])
            else:
                raise ValueError(
                    "You must provide 'user_id', 'login', or authenticate with a user token."
                )
        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="users",
            resource=User,
            params=params,
        ).get()

    def get_cheermotes(self, user_id: str = None):
        """Retrieves the list of available Cheermotes, animated emotes to which viewers can assign Bits, to cheer in chat..

        Note:
            If authenticating as a user, provide no args to get Cheermotes for authenticated user.

        Args:
            user_id (str, optional): User ID. Limit: 1.

        Returns:
            list: List containing Cheermote objects.

        """
        params = {}

        if user_id is not None:
            params["broadcaster_id"] = user_id

        if user_id is None and self.oauth_token is not None:
            validated_tokens = API(
                client_id=self.client_id,
                client_secret=self.client_secret,
                oauth_token=self.oauth_token,
                resource=User,
                path=None,
            )._get_validated_tokens()

            if "login" in validated_tokens:
                user = self.get_users(login=validated_tokens["login"])[0]
                self.get_cheermotes(user_id=user.id)
        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="bits/cheermotes",
            resource=Cheermote,
            params=params,
        ).get()
