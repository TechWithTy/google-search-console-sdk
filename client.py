"""Google Search Console SDK client.

Provides OAuth2 authentication, HTTP handling with retries, and
high-level methods for Search Analytics, Sites, and Sitemaps.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable, Optional

import requests

from .config import (
    BASE_URL_WEBMASTERS,
    HTTP_SETTINGS,
    OAUTH_SETTINGS,
    SCOPE_WEBMASTERS_READONLY,
)
from .api._exceptions import ApiError, AuthError, RateLimitError, RetryableError
from .api._requests import SearchAnalyticsQueryRequest
from .api._responses import SearchAnalyticsQueryResponse


class GSCClient:
    """Main client for Google Search Console (Webmasters v3)."""

    def __init__(
        self,
        access_token: str,
        *,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        self._access_token = access_token
        self._timeout = timeout or HTTP_SETTINGS.timeout
        self._user_agent = user_agent or HTTP_SETTINGS.user_agent
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self._access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": self._user_agent,
            }
        )

    # ----- Auth helpers (optional installed-app flow) -----
    @staticmethod
    def from_installed_app(
        *,
        client_secrets_path: Optional[str] = None,
        scopes: Optional[Iterable[str]] = None,
        token_path: Optional[str] = None,
    ) -> "GSCClient":
        """Create a client by running the Installed App OAuth2 flow.

        Requires google-auth-oauthlib and google-auth packages.
        """
        try:
            from google.oauth2.credentials import Credentials  # type: ignore
            from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
        except Exception as e:  # pragma: no cover - import-time guidance
            raise AuthError(
                "google-auth and google-auth-oauthlib are required for installed-app flow"
            ) from e

        scopes = list(scopes) if scopes else [SCOPE_WEBMASTERS_READONLY]
        client_secrets_path = client_secrets_path or OAUTH_SETTINGS.client_secrets_path
        token_path = token_path or OAUTH_SETTINGS.token_path

        creds: Optional[Credentials] = None
        # Try load existing token
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)  # type: ignore[arg-type]
        except Exception:
            creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(requests.Request())  # type: ignore[arg-type]
                except Exception:
                    creds = None
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes)
                creds = flow.run_local_server(port=0)
                try:
                    with open(token_path, "w", encoding="utf-8") as f:
                        f.write(creds.to_json())
                except Exception:
                    # Non-fatal if we can't persist
                    pass

        return GSCClient(access_token=creds.token)

    # ----- Low-level HTTP with retries -----
    def _request(self, method: str, url: str, *, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        backoff = 1.0
        max_backoff = 16.0
        attempts = 0
        while True:
            attempts += 1
            resp = self._session.request(method, url, json=json_body, timeout=self._timeout)
            if 200 <= resp.status_code < 300:
                if resp.content:
                    return resp.json()
                return {}

            # Try parse error
            try:
                err = resp.json()
                message = err.get("error", {}).get("message") or err.get("message") or resp.text
                reason = None
                if "error" in err and isinstance(err["error"], dict):
                    reasons = err["error"].get("errors") or []
                    if reasons and isinstance(reasons, list) and isinstance(reasons[0], dict):
                        reason = reasons[0].get("reason")
            except Exception:
                message = resp.text
                reason = None

            if resp.status_code == 401:
                raise AuthError(f"Unauthorized: {message}")
            if resp.status_code == 429:
                # Rate limited
                if attempts <= 5:
                    sleep_for = float(resp.headers.get("Retry-After", backoff))
                    time.sleep(sleep_for)
                    backoff = min(backoff * 2, max_backoff)
                    continue
                raise RateLimitError(resp.status_code, message, reason)
            if 500 <= resp.status_code < 600:
                if attempts <= 5:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, max_backoff)
                    continue
                raise RetryableError(resp.status_code, message, reason)

            raise ApiError(resp.status_code, message, reason)

    # ----- High-level API methods -----
    def search_analytics_query(self, site_url: str, req: SearchAnalyticsQueryRequest) -> SearchAnalyticsQueryResponse:
        url = f"{BASE_URL_WEBMASTERS}/sites/{requests.utils.quote(site_url, safe='')}/searchAnalytics/query"
        payload = req.to_dict()
        data = self._request("POST", url, json_body=payload)
        return SearchAnalyticsQueryResponse.from_dict(data)

    # Sites
    def sites_list(self) -> Dict[str, Any]:
        url = f"{BASE_URL_WEBMASTERS}/sites"
        return self._request("GET", url)

    def sites_add(self, site_url: str) -> None:
        """Register a site (property) for the current authenticated principal.

        For URL-prefix properties, pass the full URL with trailing slash, e.g. "https://dealscale.io/".
        For domain properties, pass "sc-domain:example.com".

        API returns 204 No Content on success.
        """
        url = f"{BASE_URL_WEBMASTERS}/sites/{requests.utils.quote(site_url, safe='')}"
        self._request("PUT", url)
        return None

    def sites_get(self, site_url: str) -> Dict[str, Any]:
        """Get a single site's registration and permission info for the caller."""
        url = f"{BASE_URL_WEBMASTERS}/sites/{requests.utils.quote(site_url, safe='')}"
        return self._request("GET", url)

    # Sitemaps
    def sitemaps_list(self, site_url: str) -> Dict[str, Any]:
        url = f"{BASE_URL_WEBMASTERS}/sites/{requests.utils.quote(site_url, safe='')}/sitemaps"
        return self._request("GET", url)

    def sitemaps_submit(self, site_url: str, feedpath: str) -> Dict[str, Any]:
        url = f"{BASE_URL_WEBMASTERS}/sites/{requests.utils.quote(site_url, safe='')}/sitemaps/{requests.utils.quote(feedpath, safe='')}"
        return self._request("PUT", url)

    def sitemaps_delete(self, site_url: str, feedpath: str) -> None:
        url = f"{BASE_URL_WEBMASTERS}/sites/{requests.utils.quote(site_url, safe='')}/sitemaps/{requests.utils.quote(feedpath, safe='')}"
        self._request("DELETE", url)
        return None

