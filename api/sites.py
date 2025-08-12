from __future__ import annotations

from ..client import GSCClient


def list_sites(client: GSCClient) -> dict:
    """Utility function to list sites via the SDK client."""
    return client.sites_list()
