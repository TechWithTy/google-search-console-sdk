"""Typed request models for Google Search Console API.

References:
- https://developers.google.com/webmaster-tools/v1/searchanalytics/query
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional


Dimension = Literal["DATE", "QUERY", "PAGE", "COUNTRY", "DEVICE", "SEARCH_APPEARANCE"]
Operator = Literal["EQUALS", "NOT_EQUALS", "CONTAINS", "NOT_CONTAINS"]
AggregationType = Literal["auto", "byPage", "byProperty"]
DataState = Literal["final", "all"]


@dataclass
class DimensionFilter:
    dimension: Dimension
    operator: Operator
    expression: str


@dataclass
class DimensionFilterGroup:
    filters: List[DimensionFilter]
    groupType: Literal["and", "or"] = "and"


@dataclass
class SearchAnalyticsQueryRequest:
    startDate: str  # YYYY-MM-DD
    endDate: str  # YYYY-MM-DD
    dimensions: List[Dimension] = field(default_factory=list)
    rowLimit: Optional[int] = None
    startRow: Optional[int] = None
    startDateInclusive: Optional[bool] = None  # not in spec; kept out by default
    dimensionFilterGroups: Optional[List[DimensionFilterGroup]] = None
    aggregationType: Optional[AggregationType] = None
    dataState: Optional[DataState] = None

    def to_dict(self) -> dict:
        d = {
            "startDate": self.startDate,
            "endDate": self.endDate,
        }
        if self.dimensions:
            d["dimensions"] = list(self.dimensions)
        if self.rowLimit is not None:
            d["rowLimit"] = self.rowLimit
        if self.startRow is not None:
            d["startRow"] = self.startRow
        if self.dimensionFilterGroups:
            d["dimensionFilterGroups"] = [
                {
                    "groupType": g.groupType,
                    "filters": [
                        {
                            "dimension": f.dimension,
                            "operator": f.operator,
                            "expression": f.expression,
                        }
                        for f in g.filters
                    ],
                }
                for g in self.dimensionFilterGroups
            ]
        if self.aggregationType is not None:
            d["aggregationType"] = self.aggregationType
        if self.dataState is not None:
            d["dataState"] = self.dataState
        return d

