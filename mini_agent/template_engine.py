from __future__ import annotations

from mini_agent.database_resolver import ResolvedDatabaseConfig
from mini_agent.spec import ResourceSpec


PYTHON_TYPE_MAP = {
    "str": "str",
    "string": "str",
    "text": "str",
    "int": "int",
    "integer": "int",
    "float": "float",
    "number": "float",
    "double": "float",
    "bool": "bool",
    "boolean": "bool",
}


class TemplateEngine:
    def render_env(self, db_config: ResolvedDatabaseConfig) -> str:
        return f"""MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME={db_config.database_name}
JWT_SECRET_KEY=change-this-secret
"""

    def render_core(self) -> dict[str, str]:
        return {
            "__init__.py": "",
            "core/__init__.py": "",
            "core/database.py": self._render_database(),
            "core/security.py": self._render_security(),
            "core/auth_dependencies.py": self._render_auth_dependencies(),
            "core/rbac_dependencies.py": self._render_rbac_dependencies(),
            "main.py": self._render_main_public_only(),
            "main_secure.py": self._render_main_secure_only(),
        }

    def render_auth(self) -> dict[str, str]:
        return {
            "__init__.py": "",
            "schemas.py": self._render_auth_schemas(),
            "service.py": self._render_auth_service(),
            "router.py": self._render_auth_router(),
        }

    def render_backend_module(self, spec: ResourceSpec) -> dict[str, str]:
        return {
            "schemas.py": self._render_schemas(spec),
            "crud.py": self._render_crud(spec),
            "router_public.py": self._render_router_public(spec) if "public" in spec.access_modes else "",
            "router_secure.py": self._render_router_secure(spec) if any(x in spec.access_modes for x in ("auth", "rbac")) else "",
        }

    def _render_database(self) -> str:
        return """from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "forgeapi")


@lru_cache(maxsize=1)
def get_client():
    return MongoClient(MONGODB_URL)


def get_database():
    return get_client()[DATABASE_NAME]


def get_collection(name: str):
    return get_database()[name]


def ping_database():
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False
"""

    def _render_security(self) -> str:
        return """from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret")
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_minutes: int = 60):
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
"""

    def _render_auth_dependencies(self) -> str:
        return """from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from generated.backend.core.security import decode_access_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        return decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
"""

    def _render_rbac_dependencies(self) -> str:
        return """from fastapi import Depends, HTTPException

from generated.backend.core.auth_dependencies import get_current_user


def require_permission(required_permission: str):
    def checker(current_user=Depends(get_current_user)):
        roles = current_user.get("roles", [])
        permissions = current_user.get("permissions", [])
        if "admin" in roles or "*" in permissions or required_permission in permissions:
            return current_user
        raise HTTPException(status_code=403, detail="Insufficient permission")
    return checker
"""

    def _render_main_public_only(self) -> str:
        return """from __future__ import annotations

import importlib
import json
from pathlib import Path

from fastapi import FastAPI

from generated.backend.core.database import ping_database

app = FastAPI(title="Generated API")


@app.get("/health", tags=["system"])
def health():
    db_ok = ping_database()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "mode": "public",
    }


def _should_include(module_dir: Path) -> bool:
    metadata_path = module_dir / "metadata.json"
    if not metadata_path.exists():
        return False

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception:
        return False

    access_modes = metadata.get("access_modes", [])
    return "public" in access_modes and (module_dir / "router_public.py").exists()


def load_routers():
    base = Path(__file__).parent
    for module_dir in base.iterdir():
        if not module_dir.is_dir():
            continue
        if module_dir.name in {"core", "auth", "__pycache__"}:
            continue
        if not _should_include(module_dir):
            continue

        try:
            mod = importlib.import_module(f"generated.backend.{module_dir.name}.router_public")
            app.include_router(mod.router)
        except Exception as exc:
            print(f"[WARN] Failed to load public router for {module_dir.name}: {exc}")


load_routers()
"""

    def _render_main_secure_only(self) -> str:
        return """from __future__ import annotations

import importlib
import json
from pathlib import Path

from fastapi import FastAPI

from generated.backend.core.database import ping_database

app = FastAPI(title="Generated Secure API")


@app.get("/health", tags=["system"])
def health():
    db_ok = ping_database()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "mode": "secure",
    }


def _should_include_secure(module_dir: Path) -> bool:
    metadata_path = module_dir / "metadata.json"
    if not metadata_path.exists():
        return False

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception:
        return False

    access_modes = metadata.get("access_modes", [])
    return any(x in access_modes for x in ("auth", "rbac")) and (module_dir / "router_secure.py").exists()


def load_routers():
    base = Path(__file__).parent

    auth_dir = base / "auth"
    if auth_dir.is_dir() and (auth_dir / "router.py").exists():
        try:
            auth_mod = importlib.import_module("generated.backend.auth.router")
            app.include_router(auth_mod.router)
        except Exception as exc:
            print(f"[WARN] Failed to load auth router: {exc}")

    for module_dir in base.iterdir():
        if not module_dir.is_dir():
            continue
        if module_dir.name in {"core", "auth", "__pycache__"}:
            continue
        if not _should_include_secure(module_dir):
            continue

        try:
            mod = importlib.import_module(f"generated.backend.{module_dir.name}.router_secure")
            app.include_router(mod.router)
        except Exception as exc:
            print(f"[WARN] Failed to load secure router for {module_dir.name}: {exc}")


load_routers()
"""

    def _render_auth_schemas(self) -> str:
        return """from pydantic import BaseModel, EmailStr, Field


class Signup(BaseModel):
    tenant_id: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)


class Login(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
"""

    def _render_auth_service(self) -> str:
        return """from __future__ import annotations

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
"""

    def _render_auth_router(self) -> str:
        return """from fastapi import APIRouter, HTTPException

from .schemas import Login, Signup
from .service import login, signup

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup_user(data: Signup):
    result = signup(data.model_dump())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/login")
def login_user(data: Login):
    result = login(data.model_dump())
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result
"""

    def _render_schemas(self, spec: ResourceSpec) -> str:
        class_name = spec.module_name.title()
        lines = [
            "from pydantic import BaseModel",
            "",
            f"class {class_name}Create(BaseModel):",
        ]
        for field in spec.fields:
            py_type = PYTHON_TYPE_MAP.get(field.type, "str")
            if field.required:
                lines.append(f"    {field.name}: {py_type}")
            else:
                lines.append(f"    {field.name}: {py_type} | None = None")
        return "\n".join(lines) + "\n"

    def _render_crud(self, spec: ResourceSpec) -> str:
        name = spec.module_name
        plural = self._pluralize(name)

        return f"""from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from generated.backend.core.database import get_collection


def _col():
    return get_collection("{plural}")


def _sanitize(doc):
    if not doc:
        return None
    cleaned = dict(doc)
    cleaned.pop("_id", None)
    return cleaned


def create_{name}(tenant_id, payload):
    now = datetime.now(timezone.utc).isoformat()
    data = {{
        "id": str(uuid4()),
        "tenant_id": tenant_id,
        **payload,
        "created_at": now,
        "updated_at": now,
    }}
    _col().insert_one(data)
    return _sanitize(data)


def list_{plural}(tenant_id):
    return [_sanitize(x) for x in _col().find({{"tenant_id": tenant_id}})]


def get_{name}(tenant_id, id):
    return _sanitize(_col().find_one({{"tenant_id": tenant_id, "id": id}}))
"""

    def _render_router_public(self, spec: ResourceSpec) -> str:
        class_name = spec.module_name.title()
        plural = self._pluralize(spec.module_name)
        route_prefix = f"/{plural}"

        return f"""from fastapi import APIRouter, Header, HTTPException

from .crud import create_{spec.module_name}, list_{plural}, get_{spec.module_name}
from .schemas import {class_name}Create

router = APIRouter(prefix="{route_prefix}", tags=["{spec.module_name}"])


@router.post("/")
def create_item(payload: {class_name}Create, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return create_{spec.module_name}(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items(x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return list_{plural}(x_tenant_id)


@router.get("/{{id}}")
def get_item(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    item = get_{spec.module_name}(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="{spec.module_name} not found")
    return item
"""

    def _render_router_secure(self, spec: ResourceSpec) -> str:
        class_name = spec.module_name.title()
        plural = self._pluralize(spec.module_name)
        route_prefix = f"/{plural}"

        sections: list[str] = []

        if "auth" in spec.access_modes:
            sections.append(f"""from fastapi import APIRouter, Depends, Header, HTTPException

from .crud import create_{spec.module_name}, list_{plural}, get_{spec.module_name}
from .schemas import {class_name}Create
from generated.backend.core.auth_dependencies import get_current_user

router = APIRouter(prefix="{route_prefix}", tags=["{spec.module_name}"])


@router.post("/")
def create_item_auth(payload: {class_name}Create, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    return create_{spec.module_name}(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items_auth(x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    return list_{plural}(x_tenant_id)


@router.get("/{{id}}")
def get_item_auth(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    item = get_{spec.module_name}(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="{spec.module_name} not found")
    return item
""")

        if "rbac" in spec.access_modes:
            import_block = f"""from fastapi import APIRouter, Depends, Header, HTTPException

from .crud import create_{spec.module_name}, list_{plural}, get_{spec.module_name}
from .schemas import {class_name}Create
from generated.backend.core.rbac_dependencies import require_permission
"""

            if sections:
                import_block = ""

            sections.append(f"""{import_block}
router = APIRouter(prefix="{route_prefix}", tags=["{spec.module_name}"])


@router.post("/")
def create_item_rbac(payload: {class_name}Create, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("create_{spec.module_name}"))):
    return create_{spec.module_name}(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items_rbac(x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_{spec.module_name}"))):
    return list_{plural}(x_tenant_id)


@router.get("/{{id}}")
def get_item_rbac(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_{spec.module_name}"))):
    item = get_{spec.module_name}(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="{spec.module_name} not found")
    return item
""")

        return "\n\n".join(sections) + "\n"

    def _pluralize(self, name: str) -> str:
        if name.endswith("y") and not name.endswith(("ay", "ey", "iy", "oy", "uy")):
            return f"{name[:-1]}ies"
        if name.endswith("s"):
            return name
        return f"{name}s"