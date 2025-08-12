from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from typing import Optional

from ..client import GSCClient


def get_client(authorization: Optional[str] = Header(None)) -> GSCClient:
    """Create a GSCClient from a Bearer token in the Authorization header.

    Expect header: "Authorization: Bearer <token>"
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
    token = parts[1]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty bearer token")
    return GSCClient(access_token=token)
