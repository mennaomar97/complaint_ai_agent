import os
from fastapi import Header, HTTPException
from typing import Optional

API_BEARER = os.getenv("INTERNAL_API_TOKEN")

def require_bearer(authorization: Optional[str] = Header(None)):
    if not API_BEARER:
        return  # auth disabled
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    if token != API_BEARER:
        raise HTTPException(status_code=403, detail="Invalid token")
