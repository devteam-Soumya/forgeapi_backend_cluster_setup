from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from mini_agent.database_resolver import ResolvedDatabaseConfig
from mini_agent.registry import Registry
from mini_agent.spec import ResourceSpec
from mini_agent.template_engine import TemplateEngine
from mini_agent.validator_agent import ValidatorAgent


class BackendCodegenAgent:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.generated_root = self.base_dir / "generated"
        self.backend_root = self.generated_root / "backend"
        self.core_dir = self.backend_root / "core"
        self.auth_dir = self.backend_root / "auth"
        self.template_engine = TemplateEngine()
        self.validator = ValidatorAgent()
        self.registry = Registry(str(self.base_dir))

    def generate_module(
        self,
        spec_input,
        db_config: ResolvedDatabaseConfig,
        output_dir: Optional[str] = None,
    ) -> list[Path]:
        spec = ResourceSpec.model_validate(spec_input)
        self.validator.validate_backend_spec(spec)

        if output_dir:
            self.backend_root = Path(output_dir)
            self.generated_root = self.backend_root.parent
            self.core_dir = self.backend_root / "core"
            self.auth_dir = self.backend_root / "auth"

        generated: list[Path] = []
        generated.extend(self._generate_core(db_config))

        if any(x in spec.access_modes for x in ("auth", "rbac")):
            generated.extend(self._generate_auth())

        generated.extend(self._generate_resource(spec, db_config))
        return self._dedupe_paths(generated)

    def _generate_core(self, db_config: ResolvedDatabaseConfig) -> list[Path]:
        generated: list[Path] = []

        self.generated_root.mkdir(parents=True, exist_ok=True)
        self.backend_root.mkdir(parents=True, exist_ok=True)
        self.core_dir.mkdir(parents=True, exist_ok=True)

        generated.append(self._write_file(self.generated_root / "__init__.py", ""))
        generated.append(self._write_file(self.backend_root / "__init__.py", ""))

        rendered = self.template_engine.render_core()
        for relative_name, content in rendered.items():
            generated.append(self._write_file(self.backend_root / relative_name, content))

        generated.append(
            self._write_file(self.base_dir / ".env", self.template_engine.render_env(db_config))
        )
        return self._dedupe_paths(generated)

    def _generate_auth(self) -> list[Path]:
        generated: list[Path] = []
        self.auth_dir.mkdir(parents=True, exist_ok=True)

        rendered = self.template_engine.render_auth()
        for relative_name, content in rendered.items():
            generated.append(self._write_file(self.auth_dir / relative_name, content))

        metadata = {
            "module_name": "auth",
            "access_modes": ["auth"],
            "template_key": "auth_basic",
            "display_route": "/auth",
            "enabled": True,
        }
        generated.append(self._write_json(self.auth_dir / "metadata.json", metadata))
        self.registry.register_module("auth", metadata)
        return self._dedupe_paths(generated)

    def _generate_resource(
        self,
        spec: ResourceSpec,
        db_config: ResolvedDatabaseConfig,
    ) -> list[Path]:
        generated: list[Path] = []
        module_dir = self.backend_root / spec.module_name
        module_dir.mkdir(parents=True, exist_ok=True)

        generated.append(self._write_file(module_dir / "__init__.py", ""))

        rendered = self.template_engine.render_backend_module(spec)
        for filename, content in rendered.items():
            if filename in {"router_public.py", "router_secure.py"} and not content.strip():
                continue
            generated.append(self._write_file(module_dir / filename, content))

        primary_mode = (
            "rbac"
            if "rbac" in spec.access_modes
            else "auth"
            if "auth" in spec.access_modes
            else "public"
        )

        metadata = {
            "module_name": spec.module_name,
            "tenant_id": spec.tenant_id,
            "database_mode": db_config.database_mode,
            "database_name": db_config.database_name,
            "access_modes": spec.access_modes,
            "template_keys": spec.template_keys,
            "primary_mode": primary_mode,
            "display_route": f"/{self._pluralize(spec.module_name)}",
            "collection_name": self._pluralize(spec.module_name),
            "auth_enabled": spec.auth.enabled,
            "token_required": spec.auth.token_required,
            "rbac_enabled": "rbac" in spec.access_modes,
            "permissions": {
                "create": f"create_{spec.module_name}",
                "read": f"read_{spec.module_name}",
            },
            "fields": [
                {
                    "name": field.name,
                    "type": field.type,
                    "required": field.required,
                    "unique": field.unique,
                }
                for field in spec.fields
            ],
        }

        generated.append(self._write_json(module_dir / "metadata.json", metadata))
        self.registry.register_module(spec.module_name, metadata)
        return self._dedupe_paths(generated)

    def _pluralize(self, name: str) -> str:
        if name.endswith("y") and not name.endswith(("ay", "ey", "iy", "oy", "uy")):
            return f"{name[:-1]}ies"
        if name.endswith("s"):
            return name
        return f"{name}s"

    def _write_file(self, path: Path, content: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _write_json(self, path: Path, payload: dict) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _dedupe_paths(self, paths: list[Path]) -> list[Path]:
        seen = set()
        result: list[Path] = []
        for path in paths:
            value = str(path)
            if value not in seen:
                seen.add(value)
                result.append(path)
        return result