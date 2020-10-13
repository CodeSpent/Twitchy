import requests
import json
from typing import Union
import datetime

from .utils import get_scope_list_from_string
from .resources import TwitchObject, User, Cheermote
from .exceptions import TwitchValueError, TwitchAttributeError
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

    def get_users(self, user_ids: list = None, user_logins: list = None) -> list:
        """Gets information about one or more specified Twitch users.

        Note:
            If authenticating as a user, provide no arguments to get authenticated user.

        Args:
            user_ids (list): List of Twitch User IDs. Limit: 100.
            user_logins (list): List of Twitch User Login Names. Limit: 100.

        Returns:
            list: List containing Twitch User objects.

        """

        params = {}

        if not user_ids and not user_logins:
            raise TwitchValueError("Must provide list of 'user_ids' or 'user_logins'.")

        if user_ids and len(user_ids) > 100:
            raise TwitchAttributeError("Maximum of 100 User IDs can be supplied.")
        if user_logins and len(user_logins) > 100:
            raise TwitchAttributeError("Maximum of 100 User Logins can be supplied.")

        if user_ids:
            params["id"] = user_ids
        if user_logins:
            params["login"] = user_logins

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="users",
            resource=User,
            params=params,
        ).get()

    def get_user(self, user_id: str = None, user_login: str = None) -> User:
        """Gets information about a single specificed Twitch User.

        Note:
            If authenticating as a user, provide no arguments to get the authenticated user.

        Args:
            user_id (str, optional): Twitch User ID.
            login (str, optional): Twitch User Login Name.

        Returns:
            User: A single Twitch User object.
        """
        if user_id is None and user_login is None and self.oauth_token is not None:
            validated_tokens = API(
                client_id=self.client_id,
                client_secret=self.client_secret,
                oauth_token=self.oauth_token,
                resource=User,
                path=None,
            )._get_validated_tokens()

            if "login" in validated_tokens:
                self.get_users(user_logins=[validated_tokens["login"]])
            else:
                raise TwitchValueError("Must provide a 'user_id' or 'user_login'.")
        return self.get_users(user_ids=[user_id], user_logins=[user_login])[0]

    def get_cheermotes(self, user_id: str = None) -> list:
        """Retrieves the list of available Cheermotes, animated emotes to which viewers can assign Bits, to cheer in chat..

        Note:
            If authenticating as a user, provide no args to get Cheermotes for authenticated user.

        Args:
            user_id (str, optional): User ID. Limit: 1.

        Returns:
            list: List containing Twitch Cheermote objects.

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
                user = self.get_users(user_logins=validated_tokens["login"])[0]
                self.get_cheermotes(user_id=user.id)

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="bits/cheermotes",
            resource=Cheermote,
            params=params,
        ).get()
