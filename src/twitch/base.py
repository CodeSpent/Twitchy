import time
import requests
from requests.compat import urljoin

from .constants import BASE_HELIX_URL, BASE_AUTH_URL, TOKEN_VALIDATION_URL


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

        if self._oauth_token:
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

    def _request(
        self, path=None, base_url=BASE_HELIX_URL, params={}, data={}, method="get"
    ):
        url = urljoin(base_url, path)

        # recursion issue when making a request to get oauth tokens
        # set 'use_oauth' to False for authentication calls
        use_oauth = base_url not in [BASE_AUTH_URL, TOKEN_VALIDATION_URL]
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

        response.raise_for_status()
        return response.json()


class API(TwitchAPIMixin):
    def __init__(
        self,
        client_id,
        client_secret,
        path,
        resource,
        params={},
        data=None,
        oauth_token=None,
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

    def get(self):
        response = self._request(path=self._path, method="get", params=self._params)
        return [self._resource.construct(data) for data in response["data"]]
