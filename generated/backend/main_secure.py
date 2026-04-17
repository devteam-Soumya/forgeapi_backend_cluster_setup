from __future__ import annotations

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
