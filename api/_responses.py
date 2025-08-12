"""Typed response models for Google Search Console API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SearchAnalyticsRow:
    keys: List[str]
    clicks: float
    impressions: float
    ctr: float
    position: float

    @staticmethod
    def from_dict(d: dict) -> "SearchAnalyticsRow":
        return SearchAnalyticsRow(
            keys=d.get("keys", []) or [],
            clicks=float(d.get("clicks", 0) or 0),
            impressions=float(d.get("impressions", 0) or 0),
            ctr=float(d.get("ctr", 0) or 0),
            position=float(d.get("position", 0) or 0),
        )


@dataclass
class SearchAnalyticsQueryResponse:
    rows: List[SearchAnalyticsRow]
    response_aggregation_type: Optional[str] = None

    @staticmethod
    def from_dict(d: dict) -> "SearchAnalyticsQueryResponse":
        rows = [SearchAnalyticsRow.from_dict(r) for r in d.get("rows", [])]
        return SearchAnalyticsQueryResponse(
            rows=rows,
            response_aggregation_type=d.get("responseAggregationType"),
        )

