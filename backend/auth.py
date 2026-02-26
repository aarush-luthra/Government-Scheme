"""JWT auth and role-based authorization helpers."""

from datetime import datetime, timedelta, timezone
import os
from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException, Request, status

from backend import database as db

JWT_SECRET = os.getenv("JWT_SECRET", "dev-insecure-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))


class Role:
    USER = "user"
    ADMIN = "admin"


def create_access_token(*, user_id: str, email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(*, user_id: str, email: str, role: str) -> str:
    """Create a long-lived refresh token (7 days by default)."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=JWT_REFRESH_EXPIRE_DAYS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET + "_refresh", algorithm=JWT_ALGORITHM)


def decode_refresh_token(token: str) -> dict:
    """Decode and validate a refresh token."""
    try:
        payload = jwt.decode(token, JWT_SECRET + "_refresh", algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token") from exc


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc


def _token_from_auth_header(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None
    return authorization[len(prefix):].strip()


def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(default=None),
) -> dict:
    user = resolve_user_from_request(request=request, authorization=authorization)
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


def resolve_user_from_request(
    request: Request,
    authorization: Optional[str] = None,
) -> Optional[dict]:
    # Preferred: JWT Bearer token.
    token = _token_from_auth_header(authorization)
    if token:
        payload = decode_token(token)
        user = db.get_user_by_id(str(payload.get("sub")))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

    # Backward compatibility: session cookie.
    session_id = request.cookies.get("session_id")
    if session_id:
        session = db.get_session(session_id)
        if session:
            user = db.get_user_by_email(session["email"])
            if user:
                return user

    return None


def require_role(required_role: str):
    def _guard(user: dict = Depends(get_current_user)) -> dict:
        if str(user.get("role") or Role.USER) != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _guard
