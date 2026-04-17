from __future__ import annotations

import json
import shutil
from pathlib import Path

from mini_agent.backend_codegen_agent import BackendCodegenAgent
from mini_agent.database_resolver import DatabaseResolver
from mini_agent.registry import Registry
from mini_agent.spec import ResourceSpec


class Orchestrator:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.codegen = BackendCodegenAgent(str(self.base_dir))
        self.registry = Registry(str(self.base_dir))
        self.db_resolver = DatabaseResolver()

    def create(self, spec: ResourceSpec):
        db_config = self.db_resolver.resolve(spec)
        return self.codegen.generate_module(spec, db_config=db_config)

    def delete(self, module_name: str):
        backend_root = self.base_dir / "generated" / "backend"
        target = backend_root / module_name

        deleted: list[Path] = []
        if target.exists() and target.is_dir():
            shutil.rmtree(target)
            deleted.append(target)

        self.registry.remove_module(module_name)
        return deleted

    def show(self, module_name: str) -> dict:
        module_dir = self.base_dir / "generated" / "backend" / module_name
        metadata_path = module_dir / "metadata.json"

        if not module_dir.exists():
            raise FileNotFoundError(f"Module '{module_name}' does not exist")
        if not metadata_path.exists():
            raise FileNotFoundError(f"metadata.json not found for module '{module_name}'")

        return json.loads(metadata_path.read_text(encoding="utf-8"))

    def list_modules(self) -> dict:
        return self.registry.list_modules()