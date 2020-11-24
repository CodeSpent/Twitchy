import requests
import json
from typing import Union
import datetime

from .utils import get_scope_list_from_string
from .resources import (
    TwitchObject,
    User,
    Cheermote,
    Clip,
    Game,
    HypeTrainEvent,
    BannedUser,
    BanEvent,
    ModeratorEvent,
    StreamKey,
    Stream,
    StreamMarker,
    Channel,
    Subscription,
    StreamTag,
    Follow,
    Extension,
    Video,
    WebhookSubscription,
    Commercial,
)

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
            period (str, optional): Time period over which data is aggregated  (all, day, week, or month). Defaults to "all".
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

    def get_top_games(self, first: int = 20, page_size: int = 20):
        """Retrieves the status of one or more provided bits entitlement codes.

        Note:
            Requires user authentication.

        Args:
            page_size (int, optional): Number of items per page. Default: 20. Maximum 100.

        Returns:
            list: List containing Twitch Game objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-top-games

        """
        params = {}

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="games/top",
            resource=Game,
            params=params,
            page_size=page_size,
        ).get()

    def get_games(
        self, game_ids: list = None, game_names: list = None, box_art_url: str = None
    ):
        """Retrieves game information by Game ID, Name, or Box Art URL template.

        Args:
            game_ids (list, optional): List of Game IDs. Limit: 100
            game_names (str, optional): List of Game Names. Limit: 100
            box_art_url (str, optional): Template URL for the game’s box art.

        Returns:
            list: List containing Twitch Game objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-games

        """
        params = {}

        if game_ids and len(game_ids) > 100:
            raise TwitchValueError("Maximum of 100 Game IDs may be provided.")
        elif game_ids and len(game_ids) <= 100:
            params["id"] = game_ids

        if game_names and len(game_names) > 100:
            raise TwitchValueError("Maximum of 100 Game Names may be provided.")
        elif game_names and len(game_names) <= 100:
            params["name"] = game_names

        if box_art_url:
            params["box_art_url"]

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="games",
            resource=Game,
            params=params,
        ).get()

    def get_hype_train_events(
        self,
        user_id: str = None,
        event_id: str = None,
        after: str = None,
        page_size: int = 20,
    ):
        """Gets the information of the most recent Hype Train of the specified Twitch User.

        Note:
            If authenticating as a user, provide no value for `user_id` to get authenticated user.
            After 5 days, if no Hype Train has been active, an empty list will be returned.

        Args:
            user_id (str, optional): User ID of the broadcaster.
            event_id (str, optional): ID of the event, if known.
            after (str, optional): Cursor for forward pagination.
            page_size (int, optional): Number of items per page. Default: 1. Maximum 100.

        Returns:
            list: List containing Twitch Hype Train Event objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-hype-train-events

        """
        params = {}

        if not user_id:
            # if a user id is not provided
            # get the authenticated user's id
            user = self._get_authenticated_user()
            user_id = user.id

        params["broadcaster_id"] = user_id

        if event_id:
            params["id"] = event_id

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            path="hypetrain/events",
            resource=HypeTrainEvent,
            params=params,
            oauth_token=self.oauth_token,
            page_size=page_size,
        ).get()

    def get_banned_users(self, user_ids: list = None):
        """Retrieves all currently banned and timed-out users in authenticated channel.

        Note:
            Requires user authentication and `moderation:read` scope.

        Args:
            user_ids (list, optional): List of Twitch User IDs to filter from results.

        Returns:
            list: List containing Twitch Ban objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-banned-users

        """
        params = {}

        # broadcaster_id must always match the oauth token owner
        # so rather than taking in an obvious argument, get the
        # currently authenticated user's id instead.
        user = self._get_authenticated_user()
        params["broadcaster_id"] = user.id

        if user_ids and len(user_ids) > 100:
            raise TwitchValueError("Maximum of 100 User IDs may be provided.")
        elif user_ids and len(user_ids) <= 100:
            params["user_id"] = user_ids

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            path="moderation/banned",
            oauth_token=self.oauth_token,
            params=params,
            resource=BannedUser,
        ).get()

    def get_banned_events(self, user_ids: list = None, page_size: int = 20):
        """Retrieves all user bans and un-bans in authenticated channel.

        Note:
            Requires user authentication and `moderation:read` scope.

        Args:
            user_ids (list, optional): List of Twitch User IDs to filter from results.

        Returns:
            list: List containing Twitch BanEvent objects.

        Reference:
            https://dev.twitch.tv/docs/api/reference#get-banned-users

        """
        params = {}

        # broadcaster_id must always match the oauth token owner
        # so rather than taking in an obvious argument, get the
        # currently authenticated user's id instead.
        user = self._get_authenticated_user()
        params["broadcaster_id"] = user.id

        if user_ids and len(user_ids) > 100:
            raise TwitchValueError("Maximum of 100 User IDs may be provided.")
        elif user_ids and len(user_ids) <= 100:
            params["user_id"] = user_ids

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="moderation/banned/events",
            params=params,
            resource=BanEvent,
        ).get()

    def get_moderators(self, user_ids: list = None, after: str = None):
        """Retrieves all moderators of authenticated user.

        Authorization:
            Requires user OAuth and `moderation:read` scope.

        Args:
            user_ids (list, optional): List of Twitch User IDs to filter from results. Defaults to None.
            after (str, optional): Cursor for forward pagination. Defaults to None.

        Raises:
            TwitchValueError: If length of user_ids exceeds 100.

        Returns:
            list: List containing Twitch User objects.
        """
        params = {}

        # broadcaster_id must always match the oauth token owner
        # so rather than taking in an obvious argument, get the
        # currently authenticated user's id instead.
        user = self._get_authenticated_user()
        params["broadcaster_id"] = user.id

        if user_ids and len(user_ids) > 100:
            raise TwitchValueError("Maximum of 100 User IDs may be provided.")
        elif user_ids and len(user_ids) <= 100:
            params["user_id"] = user_ids

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="moderation/moderators",
            params=params,
            resource=User,
        ).get()

    def get_moderator_events(self, user_ids: list = None):
        """Retrieves a list of moderator add/remove events.

        Authorization:
            Requires user OAuth and `moderation:read` scope.

        Args:
            user_ids (list, optional): List of Twitch User IDs to filter from results. Defaults to None.

        Raises:
            TwitchValueError: If length of user_ids exceeds 100.

        Returns:
            list: List containing Twitch ModeratorEvent objects.
        """
        params = {}

        # broadcaster_id must always match the oauth token owner
        # so rather than taking in an obvious argument, get the
        # currently authenticated user's id instead.
        user = self._get_authenticated_user()
        params["broadcaster_id"] = user.id

        if user_ids and len(user_ids) > 100:
            raise TwitchValueError("Maximum of 100 User IDs may be provided.")
        elif user_ids and len(user_ids) <= 100:
            params["user_id"] = user_ids

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="moderation/moderators/events",
            params=params,
            resource=ModeratorEvent,
        ).get()

    def get_stream_key(self):
        """Retrieves the channel stream key for an authorized user.

        Authorization:
            Requires user OAuth and `channel:read:stream_key` scope.

        Returns:
            StreamKey: A Twitch StreamKey object.
        """
        params = {}

        # broadcaster_id must always match the oauth token owner
        # so rather than taking in an obvious argument, get the
        # currently authenticated user's id instead.
        user = self._get_authenticated_user()
        params["broadcaster_id"] = user.id

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="streams/key",
            params=params,
            resource=StreamKey,
        ).get()

    def get_streams(
        self,
        user_ids: list = None,
        user_logins: list = None,
        game_ids: list = None,
        languages: list = None,
        page_size: int = 20,
    ):
        """Retrieves information about active streams sorted by current viewer count in descending order.

        Args:
            user_ids (list, optional): List of Twitch User IDs. Defaults to None. Limit 100
            user_logins (list, optional): List of Twitch User Logins. Defaults to None. Limit 100
            game_ids (list, optional): List of Twitch Game IDs. Defaults to None. Limit 100
            languages (list, optional): List of ISO 639-1 language codes. Defaults to None. Limit 100
            page_size (int, optional): Number of items per page. Defaults to 20. Maximum 100.

        Raises:
            TwitchValueError: If length of user_ids, user_logins, game_ids, or languages exceeds 100.

        Returns:
            Cursor: Iterable cursor containing Stream objects and pagination details.
        """
        params = {}

        if user_ids and len(user_ids) > 100:
            raise TwitchValueError("Maximum of 100 User IDs may be provided.")
        elif user_ids and len(user_ids) <= 100:
            params["user_id"] = user_ids

        if user_logins and len(user_logins) > 100:
            raise TwitchValueError("Maximum of 100 User Logins may be provided.")
        elif user_logins and len(user_logins) <= 100:
            params["user_login"] = user_logins

        if game_ids and len(game_ids) > 100:
            raise TwitchValueError("Maximum of 100 Game IDs may be provided.")
        elif game_ids and len(game_ids) <= 100:
            params["game_id"] = game_ids

        if languages and len(languages) > 100:
            raise TwitchValueError("Maximum of 100 Languages may be provided.")
        elif languages and len(languages) <= 100:
            params["language"] = languages

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="streams",
            params=params,
            resource=Stream,
            page_size=page_size,
        ).get()

    def get_stream_markers(
        self, user_id: str = None, video_id: str = None, page_size: int = 20
    ):
        """Retrieves a list of StreamMarker objects for specified user or video.

        Authorization:
            Requires user OAuth and `user:read:broadcast`

        Args:
            user_id (str, optional): Twitch User ID. Defaults to None.
            video_id (str, optional): Twitch Video ID. Defaults to None.
            page_size (int, optional): Number of items per page. Defaults to 20. Maximum 100.

        Returns:
            Cursor: Iterable cursor containing Stream objects and pagination details.
        """
        params = {}

        if user_id:
            params["user_id"] = user_id

        if video_id:
            params["video_id"] = video_id

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="streams/markers",
            params=params,
            resource=StreamMarker,
            page_size=page_size,
        ).get()

    def get_channel_information(self, user_id: str = None):
        """Retrieves Channel information for a specified user.

        Args:
            user_id (str, optional): Twitch User ID. Defaults to None.

        Raises:
            TwitchValueError: If no user_id is provided.

        Returns:
            Channel: A single Twitch Channel object.
        """
        if user_id:
            params = {"broadcaster_id": user_id}
        else:
            raise TwitchValueError("Must provide a `user_id`.")

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="channels",
            params=params,
            resource=Channel,
        ).get()[0]

    def get_broadcaster_subscriptions(self, user_ids: list = None):
        """Retrieves a list of users subscribed to authenticated user's channel.

        Authorization:
            Requires user OAuth token and `channel:read:subscriptions` scope.

        Args:
            user_ids (list, optional): List of Twitch User IDs to filter from results. Defaults to None.

        Raises:
            TwitchValueError: If length of user_ids exceeds 100.

        Returns:
            Cursor: Iterable cursor containing Subscription objects and pagination details.
        """

        params = {}

        if user_ids and len(user_ids) > 100:
            raise TwitchValueError("Maximum of 100 User IDs may be provided.")
        elif user_ids and len(user_ids) <= 100:
            params["user_id"] = user_ids

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="subscriptions",
            params=params,
            resource=Subscription,
        ).get()

    def get_all_stream_tags(self, tag_ids: list = None, page_size: int = 20):
        """Retrieves a list of all stream tags defined by Twitch.

        Args:
            tag_ids (list, optional): List of Twitch Tag IDs to filter from results. Defaults to None Maximum 100.
            page_size (int, optional): Number of items per page. Defaults to 20. Maximum 100.

        Raises:
            TwitchValueError: If length of user_ids exceeds 100.

        Returns:
            Cursor: Iterable cursor containing StreamTag objects and pagination details.
        """
        params = {}

        if tag_ids and len(tag_ids) > 100:
            raise TwitchValueError("Maximum of 100 tag_ids may be provided.")
        elif tag_ids and len(tag_ids) <= 100:
            # twitch accepts tag ids provided in a string
            # with tag ids separated by ampersands.
            params["tag_id"] = "&".join(tag_ids)

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="tags/streams",
            params=params,
            resource=StreamTag,
            page_size=page_size,
        ).get()

    def get_stream_tags(self, user_id: str = None):
        """Retrieves a list of stream tags for a specified channel.

        Args:
            user_id (str, optional): Twitch User ID. Defaults to None.

        Raises:
            TwitchValueError: If no user_id is provided.

        Returns:
            List: List containing StreamTag objects.
        """
        params = {}

        if user_id:
            params["broadcaster_id"] = user_id
        else:
            raise TwitchValueError("Must provide a `user_id`.")

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="streams/tags",
            params=params,
            resource=StreamTag,
        ).get()

    def get_users_follows(
        self, from_id: str = None, to_id: str = None, page_size: int = 20
    ):
        """Retrieves list of follow relationships between two users.

        Args:
            from_id (str, optional): Twitch User ID of user following. Defaults to None.
            to_id (str, optional): Twitch User ID of user being followed. Defaults to None.
            page_size (int, optional): Number of items per page. Defaults to 20. Maximum 100.

        Raises:
            TwitchValueError: If values of to_id and from_id match or neither are provided.

        Returns:
            Cursor: Iterable cursor containing Follow objects and pagination details.
        """
        params = {}

        if from_id and to_id and to_id == from_id:
            raise TwitchValueError("Value of 'to_id' cannot match 'from_id'.")

        if not from_id and not to_id:
            raise TwitchValueError("Must provide either a 'to_id', 'from_id', or both.")

        if from_id:
            params["from_id"] = from_id

        if to_id:
            params["to_id"] = to_id

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="follows",
            params=params,
            resource=Follow,
            page_size=page_size,
        ).get()

    def get_user_extensions(self):
        """Retrieves a list of all extensions (both active and inactive) for authenticated user.

        Authorization:
            Requires user OAuth and `user:read:broadcast` scope.

        Returns:
            Cursor: Iterable cursor containing Follow objects and pagination details.
        """
        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="users/extensions/list",
            resource=Extension,
        ).get()

    def get_user_active_extensions(self, user_id: str = None):
        """Retrieves a list of active extensions for a specified user.

        Authorization:
            Requires user OAuth and optionally `user:read:broadcast` or `user:edit:broadcast` scope.

        Args:
            user_id (str, optional): Twitch User ID. Defaults to None.

        Raises:
            TwitchValueError: If no user_id is provided and oauth token does not belong to a valid user.

        Returns:
            List: List containing Extension objects.
        """
        params = {}

        if not user_id:
            # if no user_id is provided, verify the oauth token is
            # for a user before proceeding
            user = self._get_authenticated_user()
            if user.id:
                user_id = user.id
            else:
                raise TwitchValueError(
                    "Must provide a 'user_id' or authenticate as a user."
                )

        params["user_id"] = user_id
        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="users/extensions",
            resource=Extension,
            params=params,
        ).get()

    def get_videos(
        self,
        video_ids: list = None,
        user_id: str = None,
        game_id: str = None,
        language: str = None,
        period: str = "all",
        sort_by: str = "time",
        type: str = "all",
        page_size: int = 20,
    ):
        """Retrieves a list of videos by video ids, or for specified user or game.

        Args:
            video_ids (list, optional): List of Twitch Video IDs. Defaults to None.
            user_id (str, optional): Twitch User ID. Defaults to None.
            game_id (str, optional): Twitch Game ID. Defaults to None.
            language (str, optional): ISO 639-1 language code. Defaults to None.
            period (str, optional): Period during which video was created (all, day, week, or month). Defaults to "all".
            sort_by (str, optional): Sort order of videos (time, trending, or views). Defaults to "time".
            type (str, optional): Type of videos to return (all, upload, archive, or highlight). Defaults to "all".
            page_size (int, optional): Number of items per page. Defaults to 20. Maximum 100.

        Raises:
            TwitchValueError: If no 'user_id', 'video_ids', or 'game_id' is provided.

        Returns:
            Cursor: Iterable cursor containing Follow objects and pagination details.
        """
        params = {}

        if not video_ids and not user_id and not game_id:
            raise TwitchValueError(
                "Must provide any combination of 'video_id', 'user_id', and/or 'game_id'."
            )

        if video_ids and len(video_ids) > 100:
            raise TwitchValueError("Maximum of 100 video user_ids can be provided.")
        elif video_ids and len(video_ids) <= 100:
            params["video_id"] = video_ids

        if user_id:
            params["user_id"] = user_id

        if game_id:
            params["game_id"] = user_id

        if language:
            params["language"] = language

        params["period"] = period
        params["sort"] = sort_by
        params["type"] = type

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="videos",
            resource=Video,
            params=params,
            page_size=page_size,
        ).get()

    def get_webhook_subscriptions(self, page_size: int = 20):
        """Retrieves list of webhook subscriptions of an authenticated app/user.

        Authorization:
            Requires User OAuth or App Access Token.

        Args:
            page_size (int, optional): Number of items per page. Defaults to 20. Maximum 100.

        Returns:
            Cursor: Iterable cursor containing Follow objects and pagination details.
        """
        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            path="webhooks/subscriptions",
            resource=WebhookSubscription,
            page_size=page_size,
        ).get()

    def start_commercial(self, length: int = 30):
        """Starts a commercial on the authenticated channel.

        Authorization:
            Requires user OAuth and `channel:edit:commercial` scope.

        Args:
            length (int, optional): Desired length of the commercial in seconds (30, 60, 90, 120, 150, or 180). Defaults to 30.

        Raises:
            TwitchValueError: If value of length is not a valid option.

        Returns:
            Commercial: A single Commercial object.
        """
        payload = {}

        # broadcaster_id must always match the oauth token owner
        # so rather than taking in an obvious argument, get the
        # currently authenticated user's id instead.
        user = self._get_authenticated_user()
        payload["broadcaster_id"] = user.id

        if length not in [30, 60, 90, 120, 150, 180]:
            raise TwitchValueError(
                "Value of 'length' must be '30', '60', '90', '120', '150', or '180'."
            )

        payload["length"] = length

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            data=payload,
            path="channels/commercial",
            resource=Commercial,
        ).post()

    def create_stream_marker(self, user_id: str = None, description: str = None):
        """Creates a StreamMarker for a specified user.

        Authorization:
            Requires User OAuth and `user:edit:broadcast` scope.

        Args:
            user_id (str, optional): Twitch User ID. Defaults to None.
            description (str, optional): Description of or comments on the marker. Max length is 140 characters. Defaults to None.

        Reference:
            https://dev.twitch.tv/docs/api/reference#create-stream-marker

        Returns:
            StreamMarker: A single StreamMarker object.

        """
        payload = {}

        if user_id is None:
            user = self._get_authenticated_user()
            user_id = user.id

        payload["user_id"] = user_id
        payload["description"] = description

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            data=payload,
            path="streams/markers",
            resource=StreamMarker,
        ).post()[0]

    def create_user_follows(
        self, from_id: str = None, to_id: str = None, allow_notifications: bool = False
    ):
        """Adds a specified user to the followers of a specific channel.

        Authorization:
            User OAuth (required)
            Scope required: user:edit:follows

        Args:
            from_id (str, optional): User ID of the follower. Defaults to None.
            to_id (str, optional): User ID of the channel to be followed. Defaults to None.
            allow_notifications (bool, optional): Whether or not to enable notifications for the user. Defaults to False.

        Raises:
            TwitchValueError: If from_id or to_id are not provided.

        Reference:
            https://dev.twitch.tv/docs/api/reference#create-user-follows

        Returns:
            None
        """
        params = {}

        if not from_id or not to_id:
            raise TwitchValueError("Must include both 'from_id' and 'to_id'.")

        params["from_id"] = from_id
        params["to_id"] = to_id
        params["allow_notifications"] = allow_notifications

        return API(
            client_id=self.client_id,
            client_secret=self.client_secret,
            oauth_token=self.oauth_token,
            params=params,
            path="users/follows",
            resource=Follow,
        ).post()
