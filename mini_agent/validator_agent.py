from __future__ import annotations

from mini_agent.spec import RESERVED_FIELD_NAMES, ResourceSpec, SUPPORTED_FIELD_TYPES


class ValidatorAgent:
    def validate_backend_spec(self, spec: ResourceSpec) -> None:
        if not spec.module_name:
            raise ValueError("module_name is required")

        if not spec.tenant_id:
            raise ValueError("tenant_id is required")

        if spec.database_mode == "different" and not spec.database_name:
            raise ValueError("database_name is required when database_mode='different'")

        seen_names: set[str] = set()
        for field in spec.fields:
            if field.name in seen_names:
                raise ValueError(f"Duplicate field name: {field.name}")
            seen_names.add(field.name)

            if field.type not in SUPPORTED_FIELD_TYPES:
                raise ValueError(f"Unsupported field type: {field.type}")

            if field.name in RESERVED_FIELD_NAMES:
                raise ValueError(f"Reserved field name is not allowed: {field.name}")

        if "rbac" in spec.access_modes and not spec.auth.token_required:
            raise ValueError("rbac access requires token_required=True")

        if "auth" in spec.access_modes and not spec.auth.token_required:
            raise ValueError("auth access requires token_required=True")