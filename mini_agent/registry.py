from __future__ import annotations

import json
from pathlib import Path


class Registry:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.registry_path = self.base_dir / ".forgeapi_registry.json"

    def _read(self) -> dict:
        if not self.registry_path.exists():
            return {"modules": {}}
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def _write(self, payload: dict) -> None:
        self.registry_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def register_module(self, module_name: str, metadata: dict) -> None:
        data = self._read()
        data.setdefault("modules", {})
        data["modules"][module_name] = metadata
        self._write(data)

    def remove_module(self, module_name: str) -> None:
        data = self._read()
        data.setdefault("modules", {})
        data["modules"].pop(module_name, None)
        self._write(data)

    def get_module(self, module_name: str) -> dict | None:
        return self._read().get("modules", {}).get(module_name)

    def list_modules(self) -> dict:
        return self._read().get("modules", {})