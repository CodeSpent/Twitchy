import time
import requests
from requests.compat import urljoin

from .constants import BASE_HELIX_URL, BASE_AUTH_URL, TOKEN_VALIDATION_URL
from .exceptions import TwitchNotProvidedError


class TwitchAPIMixin(object):
    _rate_limit_resets = set()
    _rate_limit_remaining = 0

    def _wait_for_rate_limit_reset(self):
        if self._rate_limit_remaining == 0:
            current_time = int(time.time())
            self._rate_limit_resets = set(
                x for x in self._rate_limit_resets if x > current_time
            )

            if len(self._rate_limit_resets) > 0:
                reset_time = list(self._rate_limit_resets)[0]
                time_to_wait = reset_time - current_time + 0.1
                time.sleep(time_to_wait)

    def _get_request_headers(self, use_oauth=True):
        headers = {"Client-ID": self._client_id}

        if not self._oauth_token and use_oauth is True:
            tokens = self._get_oauth_tokens()

            self._oauth_token = tokens["access_token"]
            self._token_expiration = tokens["expires_in"]

        if self._oauth_token and use_oauth is True:
            headers["Authorization"] = f"Bearer {self._oauth_token}"
        return headers

    def _get_oauth_tokens(self):
        params = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials",
        }

        response = self._request(base_url=BASE_AUTH_URL, method="post", params=params)
        response["expires_in"] = int(time.time()) + response["expires_in"]
        return response

    def _get_validated_tokens(self):
        return self._request(base_url=TOKEN_VALIDATION_URL)

    def _request(
        self, path=None, base_url=BASE_HELIX_URL, params={}, data={}, method="get"
    ):
        url = urljoin(base_url, path)

        # recursion issue when making a request to get oauth tokens
        # set 'use_oauth' to False for authentication calls
        use_oauth = base_url != BASE_AUTH_URL

        headers = self._get_request_headers(use_oauth=use_oauth)

        self._wait_for_rate_limit_reset()

        response = requests.request(
            method, url, params=params, headers=headers, data=data
        )

        remaining = response.headers.get("Ratelimit-Remaining")
        if remaining:
            self._rate_limit_remaining = int(remaining)

        reset = response.headers.get("Ratelimit-Reset")
        if reset:
            self._rate_limit_resets.add(int(reset))

        if response.status_code == 429:
            # try the request again after having executed _wait_for_limit_reset
            return self._request(path, params=params, method=method)
        elif response.status_code == 400:
            # we can expect a helpful message from twitch and relay that information
            message = response.json()["message"]

            # error meant to directly mirror structure of raise_for_status() error
            # for more predictable catching/filtering
            raise requests.exceptions.HTTPError(
                f"{response.status_code} Client Error: Bad Request for url: {response.url}: {message}"
            )

        response.raise_for_status()
        return response.json()


class API(TwitchAPIMixin):
    def __init__(
        self,
        client_id=None,
        client_secret=None,
        path=None,
        resource=None,
        params={},
        data=None,
        oauth_token=None,
        page_size=20,
        before=None,
        after=None,
    ):
        super(API, self).__init__()
        self._path = path
        self._resource = resource
        self._client_id = client_id
        self._client_secret = client_secret
        self._oauth_token = oauth_token
        self._refresh_token = None
        self._token_expiration = time.time()
        self._params = params
        self._payload = data
        self._page_size = page_size

        self._params["first"] = self._page_size

        if before is not None:
            self._params["before"] = before

        if after is not None:
            self._params["after"] = after

    def get(self):
        response = self._request(path=self._path, method="get", params=self._params)
        if "pagination" in response:
            return Cursor(
                client_id=self._client_id,
                client_secret=self._client_secret,
                oauth_token=self._oauth_token,
                path=self._path,
                resource=self._resource,
                params=self._params,
            )
        return [self._resource.construct(data) for data in response["data"]]

    def post(self):
        response = self._request(
            path=self._path, method="post", params=self._params, data=self._payload
        )
        return [self._resource.construct(data) for data in response["data"]]


class Cursor(TwitchAPIMixin):
    def __init__(
        self,
        client_id=None,
        client_secret=None,
        oauth_token=None,
        path=None,
        resource=None,
        cursor=None,
        after=None,
        before=None,
        params=None,
    ):
        super(Cursor, self).__init__()
        self._path = path
        self._queue = []
        self._cursor = cursor
        self._resource = resource
        self._client_id = client_id
        self._client_secret = client_secret
        self._oauth_token = oauth_token
        self._params = params
        self._total = None

        self.next_page()

    def __repr__(self):
        return repr(self._queue)

    def __len__(self):
        return len(self._queue)

    def __iter__(self):
        return self

    def __next__(self):
        if not self._queue:
            raise StopIteration()

        return self._queue.pop(0)

    def next_page(self):
        self._params["after"] = self._cursor

        if "before" in self._params:
            self._params.pop("before")

        return self._make_paginated_request()

    def previous_page(self):
        self._params["before"] = self._cursor

        if "after" in self._params:
            self._params.pop("after")

        return self._make_paginated_request()

    def _make_paginated_request(self):
        response = self._request(path=self._path, params=self._params, method="get")

        self._queue = [self._resource.construct(data) for data in response["data"]]
        if response["pagination"] is not None:
            self._cursor = response["pagination"].get("cursor", None)
        self._total = response.get("total", None)
        return self

    @property
    def cursor(self):
        return self._cursor

    @property
    def total(self):
        if not self._total:
            raise TwitchNotProvidedError()
        return self._total
