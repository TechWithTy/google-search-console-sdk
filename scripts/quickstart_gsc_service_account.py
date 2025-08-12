from __future__ import annotations

import os
import sys
from typing import Optional

from google.oauth2 import service_account
from google.auth.transport.requests import Request

from backend.app.core.landing_page.google_search_console import GSCClient, SearchAnalyticsQueryRequest

DEFAULT_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
SITE_URL = os.environ.get("GSC_SITE_URL", "https://dealscale.io/")
SA_KEY_PATH = os.environ.get("GSC_SA_KEY")  # path to service-account JSON
SCOPE = os.environ.get("GSC_SCOPE", DEFAULT_SCOPE)


def _get_sa_token(sa_key_path: str, scope: str) -> str:
    creds = service_account.Credentials.from_service_account_file(sa_key_path, scopes=[scope])
    creds.refresh(Request())
    return creds.token


def main() -> int:
    print("Google Search Console service-account quickstart")

    if not SA_KEY_PATH or not os.path.exists(SA_KEY_PATH):
        print("ERROR: Set GSC_SA_KEY to the path of your service-account JSON file.")
        return 2

    # 1) Get an access token for the SA
    token = _get_sa_token(SA_KEY_PATH, SCOPE)
    client = GSCClient(access_token=token)

    # 2) Ensure the SA has been added as a user on the property in Search Console UI.
    # 3) Register the site for the SA identity (no-op if already added)
    try:
        client.sites_add(SITE_URL)
        print(f"Site registered for SA: {SITE_URL}")
    except Exception as e:
        # 204 No Content on success; if already added, sites_get should succeed.
        print("sites_add warning/skip:", e)

    # Verify registration/permission
    try:
        info = client.sites_get(SITE_URL)
        print("Site info:", info)
    except Exception as e:
        print("ERROR: sites_get failed. Confirm the SA is added as a user on the property and SITE_URL matches property type.")
        print(e)
        return 1

    # 4) Run a small query (last 7 days)
    req = SearchAnalyticsQueryRequest(startDate="2025-08-05", endDate="2025-08-12", rowLimit=10)
    try:
        resp = client.search_analytics_query(SITE_URL, req)
    except Exception as e:
        print("Query failed:", e)
        return 1

    print(f"Got {len(resp.rows)} rows for {SITE_URL}")
    for i, row in enumerate(resp.rows, start=1):
        print(i, row.keys, row.clicks, row.impressions, row.ctr, row.position)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
