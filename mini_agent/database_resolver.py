from __future__ import annotations

from dataclasses import dataclass

from mini_agent.spec import ResourceSpec


@dataclass
class ResolvedDatabaseConfig:
    tenant_id: str
    database_mode: str
    database_name: str


class DatabaseResolver:
    def resolve(self, spec: ResourceSpec) -> ResolvedDatabaseConfig:
        if spec.database_mode == "same":
            db_name = f"tenant_{spec.tenant_id}_db"
        else:
            db_name = spec.database_name or f"tenant_{spec.tenant_id}_custom_db"

        return ResolvedDatabaseConfig(
            tenant_id=spec.tenant_id,
            database_mode=spec.database_mode,
            database_name=db_name,
        )