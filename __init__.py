"""Google Search Console SDK (Webmasters v3).

Public surface:
- GSCClient: main client
- SearchAnalyticsQueryRequest and response types
"""

from .client import GSCClient
from .api._requests import SearchAnalyticsQueryRequest, DimensionFilter, DimensionFilterGroup
from .api._responses import SearchAnalyticsQueryResponse

__all__ = [
    "GSCClient",
    "SearchAnalyticsQueryRequest",
    "SearchAnalyticsQueryResponse",
    "DimensionFilter",
    "DimensionFilterGroup",
]
