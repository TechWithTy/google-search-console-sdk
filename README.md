# CyberOni Google Search Console SDK (Python)

Utilities and a lightweight client for the Google Search Console (Webmasters v3) API. Includes typed models, retrying HTTP logic, and quickstart scripts for both installed-app (interactive) and service-account (server) authentication.

- Folder: `backend/app/core/landing_page/google_search_console/`
- Main client: `client.py` exposing `GSCClient`
- Models: `api/_requests.py`, `api/_responses.py`
- Helpers: `api/sitemaps.py` utilities
- Scripts: `scripts/quickstart_gsc.py`, `scripts/quickstart_gsc_service_account.py`

## Features
- OAuth2 authentication (installed app or service account)
- Search Analytics query with typed request/response models
- Sites and Sitemaps helpers (`sites_list`, `sites_add`, `sites_get`, `sitemaps_*`)
- Robust HTTP error handling with retries/backoff

## Requirements
- Python 3.10+
- Enabled API in your Google Cloud project: `webmasters.googleapis.com` (Search Console API)
- Search Console access to the property (your user or your service account must be a user/owner)

## Installation

Using `uv` in this subfolder (recommended):
```bash
# from: backend/app/core/landing_page/google_search_console/
uv pip install -e .
```

Or with pip:
```bash
# from: backend/app/core/landing_page/google_search_console/
pip install -e .
```

Dependencies are defined in `pyproject.toml`:
- `requests`, `google-auth`, `google-auth-oauthlib`, `pydantic`, `pytest` (dev)

## Environment variables
Copy `.env.example` and fill real values (Windows paths are fine):

```dotenv
# Installed-app OAuth (optional for local interactive)
GSC_CLIENT_SECRETS=C:\secrets\gsc\client_secrets.json
GSC_TOKEN_PATH=./.gsc_token.json

# Service Account (server/CI)
GSC_SA_KEY=C:\secrets\gsc\analytics-deal-scale.json
GSC_SCOPE=https://www.googleapis.com/auth/webmasters.readonly

# Property identifier (must match property type EXACTLY)
# URL-prefix example (note trailing slash): https://dealscale.io/
# Domain property example: sc-domain:dealscale.io
GSC_SITE_URL=https://dealscale.io/

# Optional HTTP tweaks
GSC_HTTP_TIMEOUT=30
GSC_USER_AGENT=DealScale-GSC-SDK/1.0
```

How to determine `GSC_SITE_URL`:
- If your property type in Search Console is URL-prefix, use the full URL with scheme and trailing slash, e.g. `https://dealscale.io/`.
- If it is a Domain property, use `sc-domain:dealscale.io`.
- You can also run `client.sites_list()` and copy the `siteUrl` value shown.

## Authentication options

### A) Installed-app OAuth (interactive; easiest for local)
1) In Google Cloud Console: configure OAuth consent screen, create an OAuth Client of type "Desktop app" and download its JSON.
2) Set `GSC_CLIENT_SECRETS` (and optionally `GSC_TOKEN_PATH`).
3) Run the quickstart:
```bash
# from repo root, module path assumes CWD is backend/
python -m app.core.landing_page.google_search_console.scripts.quickstart_gsc
```
- First run opens a browser for sign-in; token is cached. Subsequent runs are silent.

### B) Service account (server/CI; headless)
1) Create a Service Account and JSON key in your Google Cloud project.
2) In Search Console UI for your property, add the SA email as a user (Settings → Users and permissions → Add user).
3) Ensure API `webmasters.googleapis.com` is enabled in the same project.
4) Set env vars and run the quickstart:
```bash
# PowerShell example (Windows)
$env:GSC_SA_KEY="C:\secrets\gsc\analytics-deal-scale.json"
$env:GSC_SITE_URL="https://dealscale.io/"   # or sc-domain:dealscale.io
$env:GSC_SCOPE="https://www.googleapis.com/auth/webmasters.readonly"

# from repo root, set CWD to backend so app.* resolves
python -m app.core.landing_page.google_search_console.scripts.quickstart_gsc_service_account
```
What the script does:
- Exchanges SA key for an access token.
- Registers the site for the SA (`client.sites_add()`), then verifies (`client.sites_get()`).
- Runs a short Search Analytics query and prints rows.

## Programmatic usage examples

```python
from backend.app.core.landing_page.google_search_console import GSCClient, SearchAnalyticsQueryRequest

# If you already have an OAuth access token (e.g., service account):
client = GSCClient(access_token="<ACCESS_TOKEN>")

# List sites
print(client.sites_list())

# Query Search Analytics
req = SearchAnalyticsQueryRequest(
    startDate="2025-07-01",
    endDate="2025-07-31",
    dimensions=["QUERY", "PAGE"],
    rowLimit=50,
)
resp = client.search_analytics_query("https://dealscale.io/", req)
print(len(resp.rows), "rows")

# Sitemaps
print(client.sitemaps_list("https://dealscale.io/"))
client.sitemaps_submit("https://dealscale.io/", "sitemap.xml")
client.sitemaps_delete("https://dealscale.io/", "sitemap.xml")
```

## Troubleshooting
- **401 Unauthorized**
  - Token expired/invalid; re-auth.
  - Service account not added as a user on the property.
- **403 Forbidden: insufficient permissions**
  - The identity (user or SA) lacks permission on the property. Add it in Search Console Settings.
- **Site URL mismatch**
  - `GSC_SITE_URL` must match the property type exactly. URL-prefix requires scheme and trailing slash; domain uses `sc-domain:`.
- **API not visible / can't enable**
  - Ensure the correct project. Org policy may restrict consumer APIs; ask an admin or use a personal project.
- **Org blocks SA keys**
  - Use installed-app OAuth locally, or set up Workload/Workforce Identity Federation (WIF) for keyless auth.
- **Leaked SA key**
  - Immediately delete/rotate the key in Cloud Console. Never commit keys to VCS.

## Dev and tests
- Unit tests (HTTP mocked) live in `_tests/` and can be run via:
```bash
pytest backend/app/core/landing_page/google_search_console/_tests -q
```

## Security
- Treat all credential files as secrets; do not commit to git.
- Use least-privilege scopes (`webmasters.readonly` unless you need write operations).

## License
Internal DealScale component. Replace with your preferred license if extracted as a submodule/repo.
