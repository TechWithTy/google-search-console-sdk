from __future__ import annotations

from pydantic import BaseModel

from ..client import GSCClient


class SubmitBody(BaseModel):
    siteUrl: str
    feedpath: str


def list_sitemaps_util(client: GSCClient, siteUrl: str) -> dict:
    return client.sitemaps_list(siteUrl)


def submit_sitemap_util(client: GSCClient, body: SubmitBody) -> dict:
    return client.sitemaps_submit(body.siteUrl, body.feedpath)


def delete_sitemap_util(client: GSCClient, siteUrl: str, feedpath: str) -> dict:
    client.sitemaps_delete(siteUrl, feedpath)
    return {"status": "deleted"}
