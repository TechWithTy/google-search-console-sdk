from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, Dict

import pytest

from app.core.landing_page.google_search_console.client import GSCClient
from app.core.landing_page.google_search_console.api._requests import SearchAnalyticsQueryRequest


class _Resp:
    def __init__(self, status_code: int, data: Dict[str, Any], headers: Dict[str, str] | None = None):
        self.status_code = status_code
        self._data = data
        self.headers = headers or {}
        self.content = json.dumps(data).encode("utf-8") if data else b""
        self.text = json.dumps(data)

    def json(self) -> Dict[str, Any]:
        return self._data


@pytest.fixture()
def client() -> GSCClient:
    # Direct token; no google-auth required
    return GSCClient(access_token="test-token")


def test_search_analytics_query_success(monkeypatch: pytest.MonkeyPatch, client: GSCClient):
    # Arrange a fake HTTP response
    data = {
        "rows": [
            {"keys": ["query A", "/"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 3.2},
            {"keys": ["query B", "/page"], "clicks": 5, "impressions": 50, "ctr": 0.1, "position": 5.0},
        ],
        "responseAggregationType": "auto",
    }

    def fake_request(method: str, url: str, json: dict | None = None, timeout: int | float | None = None):
        return _Resp(200, data)

    # Patch only this client's session
    client._session.request = fake_request  # type: ignore[attr-defined]

    req = SearchAnalyticsQueryRequest(
        startDate="2025-07-01",
        endDate="2025-07-31",
        dimensions=["QUERY", "PAGE"],
        rowLimit=250,
    )

    # Act
    resp = client.search_analytics_query("https://example.com/", req)

    # Assert
    assert len(resp.rows) == 2
    assert resp.rows[0].keys == ["query A", "/"]
    assert resp.rows[0].clicks == 10
    assert resp.response_aggregation_type == "auto"


def test_search_analytics_query_retry_on_429(monkeypatch: pytest.MonkeyPatch, client: GSCClient):
    # Arrange first 429 then 200
    calls = {"n": 0}
    data_ok = {"rows": [], "responseAggregationType": "auto"}

    def fake_request(method: str, url: str, json: dict | None = None, timeout: int | float | None = None):
        calls["n"] += 1
        if calls["n"] == 1:
            return _Resp(429, {"error": {"message": "rate limit"}}, headers={"Retry-After": "0"})
        return _Resp(200, data_ok)

    client._session.request = fake_request  # type: ignore[attr-defined]

    # Avoid real sleep during backoff
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    req = SearchAnalyticsQueryRequest(startDate="2025-07-01", endDate="2025-07-31")

    # Act
    resp = client.search_analytics_query("https://example.com/", req)

    # Assert
    assert calls["n"] == 2
    assert resp.rows == []
