"""
Google Search Console SDK configuration.

Defines constants, default settings, and simple env-driven configuration
for OAuth2 credentials and token storage.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


# REST bases
BASE_URL_WEBMASTERS = "https://www.googleapis.com/webmasters/v3"
BASE_URL_URL_INSPECTION = "https://searchconsole.googleapis.com/v1"

# Scopes
SCOPE_WEBMASTERS_READONLY = "https://www.googleapis.com/auth/webmasters.readonly"
SCOPE_WEBMASTERS = "https://www.googleapis.com/auth/webmasters"

# Defaults
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_USER_AGENT = "deal-scale-gsc-sdk/0.1"


@dataclass(frozen=True)
class OAuthSettings:
    """Location of client secrets and token cache.

    Env overrides:
      - GSC_CLIENT_SECRETS: path to OAuth client_secrets.json
      - GSC_TOKEN_PATH: path to token storage file (JSON)
    """

    client_secrets_path: str = os.getenv("GSC_CLIENT_SECRETS", "./client_secrets.json")
    token_path: str = os.getenv("GSC_TOKEN_PATH", "./.gsc_token.json")


@dataclass(frozen=True)
class HttpSettings:
    timeout: int = int(os.getenv("GSC_HTTP_TIMEOUT", str(DEFAULT_TIMEOUT)))
    user_agent: str = os.getenv("GSC_USER_AGENT", DEFAULT_USER_AGENT)


OAUTH_SETTINGS = OAuthSettings()
HTTP_SETTINGS = HttpSettings()

