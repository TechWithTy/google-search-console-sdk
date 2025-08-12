from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel

from ..client import GSCClient
from ..api._requests import SearchAnalyticsQueryRequest as SARequest
from ..api._responses import SearchAnalyticsQueryResponse


# Pydantic schemas for reusability in services/tests
Dimension = Literal["DATE", "QUERY", "PAGE", "COUNTRY", "DEVICE", "SEARCH_APPEARANCE"]
Operator = Literal["EQUALS", "NOT_EQUALS", "CONTAINS", "NOT_CONTAINS"]
AggregationType = Literal["auto", "byPage", "byProperty"]
DataState = Literal["final", "all"]


class DimensionFilter(BaseModel):
    dimension: Dimension
    operator: Operator
    expression: str


class DimensionFilterGroup(BaseModel):
    filters: List[DimensionFilter]
    groupType: Literal["and", "or"] = "and"


class SearchAnalyticsQueryBody(BaseModel):
    siteUrl: str
    startDate: str
    endDate: str
    dimensions: Optional[List[Dimension]] = None
    rowLimit: Optional[int] = None
    startRow: Optional[int] = None
    dimensionFilterGroups: Optional[List[DimensionFilterGroup]] = None
    aggregationType: Optional[AggregationType] = None
    dataState: Optional[DataState] = None


def search_analytics_query_util(client: GSCClient, body: SearchAnalyticsQueryBody) -> dict:
    """Utility function wrapping GSCClient.search_analytics_query.

    Returns a plain dict convenient for JSON serialization.
    """
    # map Pydantic -> dataclass
    df_groups = None
    if body.dimensionFilterGroups:
        from ..api._requests import DimensionFilter as DF, DimensionFilterGroup as DFG

        df_groups = [
            DFG(
                filters=[DF(dimension=f.dimension, operator=f.operator, expression=f.expression) for f in g.filters],
                groupType=g.groupType,
            )
            for g in body.dimensionFilterGroups
        ]

    req = SARequest(
        startDate=body.startDate,
        endDate=body.endDate,
        dimensions=list(body.dimensions or []),
        rowLimit=body.rowLimit,
        startRow=body.startRow,
        dimensionFilterGroups=df_groups,
        aggregationType=body.aggregationType,
        dataState=body.dataState,
    )
    resp: SearchAnalyticsQueryResponse = client.search_analytics_query(body.siteUrl, req)

    return {
        "rows": [
            {
                "keys": r.keys,
                "clicks": r.clicks,
                "impressions": r.impressions,
                "ctr": r.ctr,
                "position": r.position,
            }
            for r in resp.rows
        ],
        "responseAggregationType": resp.response_aggregation_type,
    }
