from __future__ import annotations

import json
from typing import Any, Dict

import pytest

from app.core.landing_page.google_search_console.client import GSCClient
from app.core.landing_page.google_search_console.api.sitemaps import (
    list_sitemaps_util,
    submit_sitemap_util,
    delete_sitemap_util,
    SubmitBody,
)


class _Resp:
    def __init__(self, status_code: int, data: Dict[str, Any] | None, headers: Dict[str, str] | None = None):
        self.status_code = status_code
        self._data = data or {}
        self.headers = headers or {}
        self.content = json.dumps(self._data).encode("utf-8") if self._data else b""
        self.text = json.dumps(self._data)

    def json(self) -> Dict[str, Any]:
        return self._data


@pytest.fixture()
def client() -> GSCClient:
    return GSCClient(access_token="test-token")


def test_sites_list_success(client: GSCClient):
    # Arrange
    sites_payload = {
        "siteEntry": [
            {"siteUrl": "https://example.com/", "permissionLevel": "siteOwner"},
            {"siteUrl": "sc-domain:example.com", "permissionLevel": "siteRestrictedUser"},
        ]
    }

    def fake_request(method: str, url: str, json: dict | None = None, timeout: int | float | None = None):
        assert method == "GET"
        assert url.endswith("/sites")
        return _Resp(200, sites_payload)

    client._session.request = fake_request  # type: ignore[attr-defined]

    # Act
    result = client.sites_list()

    # Assert
    assert "siteEntry" in result
    assert len(result["siteEntry"]) == 2


def test_sitemaps_list_submit_delete(client: GSCClient):
    calls: list[str] = []
    site_url = "https://example.com/"
    feed = "sitemap.xml"

    def fake_request(method: str, url: str, json: dict | None = None, timeout: int | float | None = None):
        calls.append(f"{method} {url}")
        if method == "GET":
            return _Resp(200, {"sitemap": []})
        if method == "PUT":
            return _Resp(200, {"status": "submitted"})
        if method == "DELETE":
            return _Resp(204, None)
        raise AssertionError("Unexpected method")

    client._session.request = fake_request  # type: ignore[attr-defined]

    # list
    out = list_sitemaps_util(client, site_url)
    assert out == {"sitemap": []}

    # submit
    out2 = submit_sitemap_util(client, SubmitBody(siteUrl=site_url, feedpath=feed))
    assert out2 == {"status": "submitted"}

    # delete
    out3 = delete_sitemap_util(client, site_url, feed)
    assert out3 == {"status": "deleted"}

    assert any(x.startswith("GET ") for x in calls)
    assert any(x.startswith("PUT ") for x in calls)
    assert any(x.startswith("DELETE ") for x in calls)


def test_auth_unauthorized_raises(client: GSCClient):
    def fake_request(method: str, url: str, json: dict | None = None, timeout: int | float | None = None):
        return _Resp(401, {"error": {"message": "Unauthorized"}})

    client._session.request = fake_request  # type: ignore[attr-defined]

    with pytest.raises(Exception) as exc:
        client.sites_list()
    assert "Unauthorized" in str(exc.value)
