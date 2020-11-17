import requests
import json
from typing import Union
import datetime

from .utils import get_scope_list_from_string
from .resources import TwitchObject, User, Cheermote, Clip, Game
from .exceptions import TwitchValueError
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

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-users

        """

        params = {}

        if not user_ids and not user_logins:
            raise TwitchValueError("Must provide list of 'user_ids' or 'user_logins'.")

        if user_ids and len(user_ids) > 100:
            raise TwitchValueError("Maximum of 100 User IDs can be supplied.")
        if user_logins and len(user_logins) > 100:
            raise TwitchValueError("Maximum of 100 User Logins can be supplied.")

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

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-users
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
            list: List containing Twitch Cheermote objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-cheermotes
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
        ended_at: str = None,
        page_size: int = 20,
    ) -> list:
        """Retrieves a list of clips for a specified User, Game, or Clip ID.

        Note:
            If authenticating as a user, provide no args to get Clips for authenticated user.
            If 'started_at' or 'ended_at' are specified, both must be provided; otherwise, the ended_at date/time will be 1 week after the started_at value.

        Args:
            user_id (str, optional): User ID. Limit: 1.
            game_id (str, optional): Game ID. Limit 1.
            clip_id (str, optional): Clip ID. Limit 1.
            before (str, optional): Cursor for backward pagination.
            after (str, optional): Cursor for forward pagination.
            started_at (str, optional): Starting date/time for returned clips, in RFC3339 format. (Note that the seconds value is ignored.)
            ended_at (str, optional): Ending date/time for returned clips, in RFC3339 format. (Note that the seconds value is ignored.)
            page_size (int, optional): Number of items per page. Default: 20. Maximum 100.

        Returns:
            list: List containing Twitch Clip objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-clips

        """
        params = {}

        if user_id:
            params["broadcaster_id"] = user_id
        if game_id:
            params["game_id"] = game_id
        if clip_id:
            params["id"] = clip_id
        if started_at:
            params["started_at"] = started_at
        if ended_at:
            params["ended_at"] = ended_at

        if not user_id and not game_id and not clip_id and self.oauth_token:
            user = self._get_authenticated_user()
            return self.get_clips(user_id=user.id)
        elif not user_id and not game_id and not clip_id and not self.oauth_token:
            raise TwitchValueError(
                "Must provide 'user_id', 'game_id', 'clip_id', or authenticate as a user."
            )

        if page_size and page_size > 100:
            raise TwitchValueError(
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

    def get_bits_leaderboard(
        self,
        count: int = 10,
        period: str = "all",
        started_at: str = None,
        user_id: str = None,
        page_size: int = 20,
    ) -> list:
        """Retrieves a ranked list of Bits leaderboard information for an authorized broadcaster.

        Note:
            Requires user authentication and `bits:read` scope.

        Args:
            count (int, optional): Number of results to be returned. Maximum: 100. Default: 10.
            period (str, optional): Time period over which data is aggregated (PST time zone). This parameter interacts with `started_at`.
            started_at (str, optional): Starting date/time for returned clips, in RFC3339 format. (Note that the seconds value is ignored.)
            user_id (str, optional): ID of the user whose results are returned.
            page_size (int, optional): Default 20.

        Returns:
            list: List containing Twitch objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-bits-leaderboard

        """
        params = {}

        if count > 100:
            raise TwitchValueError("Value of 'count' must be equal or less than 100.")
        if period not in ["day", "week", "month", "year", "all"]:
            raise TwitchValueError(
                "Value of 'period' must be 'day', 'week', 'month', 'year', or 'all'."
            )

        params["count"] = count
        params["period"] = period

        if started_at:
            params["started_at"] = started_at
        if user_id:
            params["user_id"] = user_id

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            path="bits/leaderboard",
            resource=TwitchObject,
            params=params,
            oauth_token=self.oauth_token,
            page_size=page_size,
        ).get()

    def get_code_status(self, codes: list = None, user_id: str = None):
        """Retrieves the status of one or more provided bits entitlement codes.

        Note:
            Requires user authentication.

        Args:
            codes (list): List of codes to get the status of. Limit: 20.
            user_id (str): Twitch user id which is going to receive the entitlement associated with the code.

        Returns:
            list: List containing Twitch objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-code-status

        """
        params = {}

        if not codes or len(codes) == 0:
            raise TwitchValueError("Must provide at least 1 code.")
        elif codes and len(codes) > 20:
            raise TwitchValueError("Maximum of 20 codes may be supplied.")
        elif codes and len(codes) <= 20:
            params["code"] = codes

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="entitlements/codes",
            resource=TwitchObject,
            params=params,
        ).get()

    def get_top_games(
        self,
        after: str = None,
        before: str = None,
        first: int = 20,
        page_size: int = 20,
    ):
        """Retrieves the status of one or more provided bits entitlement codes.

        Note:
            Requires user authentication.

        Args:
            before (str, optional): Cursor for backward pagination.
            after (str, optional): Cursor for forward pagination.
            page_size (int, optional): Number of items per page. Default: 20. Maximum 100.

        Returns:
            list: List containing Twitch Game objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-top-games

        """
        params = {"after": after, "before": before}

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="games/top",
            resource=Game,
            params=params,
            page_size=page_size,
        ).get()
