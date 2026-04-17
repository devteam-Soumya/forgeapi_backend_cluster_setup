from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from generated.backend.core.database import get_collection


def _col():
    return get_collection("categories")


def _sanitize(doc):
    if not doc:
        return None
    cleaned = dict(doc)
    cleaned.pop("_id", None)
    return cleaned


def create_category(tenant_id, payload):
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "id": str(uuid4()),
        "tenant_id": tenant_id,
        **payload,
        "created_at": now,
        "updated_at": now,
    }
    _col().insert_one(data)
    return _sanitize(data)


def list_categories(tenant_id):
    return [_sanitize(x) for x in _col().find({"tenant_id": tenant_id})]


def get_category(tenant_id, id):
    return _sanitize(_col().find_one({"tenant_id": tenant_id, "id": id}))
