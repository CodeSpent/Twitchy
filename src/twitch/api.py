import requests
import json
from typing import Union
import datetime

from .utils import get_scope_list_from_string
from .resources import TwitchObject, User, Cheermote, Clip
from .exceptions import TwitchValueError, TwitchAttributeError
from .base import API, Cursor


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

    def _get_authenticated_user(self):
        validated_tokens = API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            resource=User,
            path=None,
        )._get_validated_tokens()

        if "login" in validated_tokens:
            return self.get_user(user_login=validated_tokens["login"])

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
            return self._get_authenticated_user()
        elif user_id is None and user_login is None and self.oauth_token is None:
            raise TwitchValueError(
                "Must provide a 'user_id' or 'user_login' or authenticate as a user."
            )
        else:
            return self.get_users(user_ids=[user_id], user_logins=[user_login])[0]

    def get_cheermotes(self, user_id: str = None) -> list:
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
            user = self._get_authenticated_user()
            self.get_cheermotes(user_id=user.id)

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="bits/cheermotes",
            resource=Cheermote,
            params=params,
        ).get()

    def get_clips(
        self,
        user_id: str = None,
        game_id: str = None,
        clip_id: str = None,
        before: str = None,
        after: str = None,
        started_at: str = None,
        page_size: int = 20,
    ) -> list:
        """Retrieves a list of clips for a specified User, Game, or Clip ID.

        Note:
            If authenticating as a user, provide no args to get Clips for authenticated user.

        Args:
            user_id (str, optional): User ID. Limit: 1.
            game_id (str, optional): Game ID. Limit 1.
            clip_id (str, optional): Clip ID. Limit 1.
            before (str, optional): Cursor for backward pagination.
            after (str, optional): Cursor for forward pagination.
            page_size (int, optional): Number of items per page. Default: 20. Maximum 100.


        Returns:
            list: List containing Twitch Clip objects.

        """
        params = {}

        if user_id:
            params["broadcaster_id"] = user_id
        if game_id:
            params["game_id"] = game_id
        if clip_id:
            params["id"] = clip_id

        if not user_id and not game_id and not clip_id:
            user = self._get_authenticated_user()
            return self.get_clips(user_id=user.id)

        if page_size and page_size > 100:
            raise TwitchAttributeError(
                "Value of 'page_size' must be less than or equal to 100."
            )

        # the clips endpoint demonstrated an off by one error
        # relating to the 'first' param. If this is evident on
        # other endpoints, this should be set in API __init__.
        page_size = page_size + 1

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="clips",
            resource=Clip,
            params=params,
            page_size=page_size,
        ).get()
