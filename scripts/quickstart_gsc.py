from __future__ import annotations

import os
import sys
from datetime import date, timedelta

from backend.app.core.landing_page.google_search_console import (
    GSCClient,
    SearchAnalyticsQueryRequest,
)

SITE_URL = os.environ.get("GSC_SITE_URL", "https://dealscale.io/")


def main() -> int:
    print("Google Search Console quickstart")

    # Ensure client secrets path is set
    client_secrets = os.environ.get("GSC_CLIENT_SECRETS")
    if not client_secrets or not os.path.exists(client_secrets):
        print("ERROR: Set GSC_CLIENT_SECRETS to your OAuth client JSON path.")
        return 2

    # Build client using installed-app OAuth flow
    client = GSCClient.from_installed_app()

    # 1) List sites to verify access
    sites = client.sites_list()
    print("Sites:", sites)

    # 2) Query last 28 days of Search Analytics for SITE_URL
    end = date.today()
    start = end - timedelta(days=28)
    req = SearchAnalyticsQueryRequest(
        startDate=start.isoformat(),
        endDate=end.isoformat(),
        dimensions=["QUERY", "PAGE"],
        rowLimit=25,
    )

    try:
        resp = client.search_analytics_query(SITE_URL, req)
    except Exception as e:
        print("Query failed:", e)
        return 1

    print(f"Got {len(resp.rows)} rows for {SITE_URL}")
    for i, row in enumerate(resp.rows[:10], start=1):
        print(i, row.keys, row.clicks, row.impressions, row.ctr, row.position)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
