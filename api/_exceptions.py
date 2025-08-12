"""Custom exceptions for the Google Search Console SDK."""

from __future__ import annotations

from typing import Any, Dict, Optional


class GSCError(Exception):
    """Base exception type for SDK errors."""


class AuthError(GSCError):
    """Authentication or authorization error."""


class ApiError(GSCError):
    """Represents an error returned by Google's API."""

    def __init__(self, status: int, message: str, reason: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status = status
        self.reason = reason
        self.details = details or {}

    def __str__(self) -> str:
        base = f"API Error {self.status}: {super().__str__()}"
        if self.reason:
            base += f" (reason={self.reason})"
        return base


class RateLimitError(ApiError):
    """HTTP 429 Too Many Requests or quota exceeded."""


class RetryableError(ApiError):
    """Transient HTTP 5xx errors that can be retried."""

