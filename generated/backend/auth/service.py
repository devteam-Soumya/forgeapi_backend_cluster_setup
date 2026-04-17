from __future__ import annotations

from datetime import datetime, timezone

import bcrypt

from generated.backend.core.database import get_collection
from generated.backend.core.security import create_access_token


def _users():
    return get_collection("users")


def _sanitize_user(user):
    if not user:
        return None
    cleaned = dict(user)
    cleaned.pop("_id", None)
    cleaned.pop("password_hash", None)
    return cleaned


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def signup(data):
    existing = _users().find_one({"email": data["email"]})
    if existing:
        return {"error": "user_exists"}

    now = datetime.now(timezone.utc).isoformat()
    record = {
        "tenant_id": data["tenant_id"],
        "email": data["email"],
        "password_hash": _hash_password(data["password"]),
        "roles": ["admin"],
        "permissions": ["*"],
        "created_at": now,
        "updated_at": now,
    }
    _users().insert_one(record)
    return {"created": True, "user": _sanitize_user(record)}


def login(data):
    user = _users().find_one({"email": data["email"]})
    if not user:
        return {"error": "invalid_credentials"}

    if not _verify_password(data["password"], user["password_hash"]):
        return {"error": "invalid_credentials"}

    token_payload = {
        "sub": user["email"],
        "tenant_id": user.get("tenant_id"),
        "roles": user.get("roles", []),
        "permissions": user.get("permissions", []),
    }

    return {
        "access_token": create_access_token(token_payload),
        "token_type": "bearer",
        "user": _sanitize_user(user),
    }
