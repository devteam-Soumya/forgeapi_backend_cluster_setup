from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


SUPPORTED_FIELD_TYPES = {
    "str",
    "string",
    "text",
    "int",
    "integer",
    "float",
    "number",
    "double",
    "bool",
    "boolean",
}

RESERVED_FIELD_NAMES = {
    "id",
    "_id",
    "tenant_id",
    "created_at",
    "updated_at",
}


class AuthSpec(BaseModel):
    enabled: bool = False
    token_required: bool = False


class FieldSpec(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    required: bool = True
    unique: bool = False

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field name cannot be empty")
        if " " in value:
            raise ValueError("Field name must not contain spaces")
        if not value.replace("_", "").isalnum():
            raise ValueError("Field name must be alphanumeric with optional underscores")
        if value[0].isdigit():
            raise ValueError("Field name cannot start with a digit")
        return value

    @field_validator("type")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in SUPPORTED_FIELD_TYPES:
            raise ValueError(
                f"Unsupported field type: {value}. Supported types: {sorted(SUPPORTED_FIELD_TYPES)}"
            )
        return value


class ResourceSpec(BaseModel):
    module_name: str = Field(..., min_length=1)
    access_modes: list[Literal["public", "auth", "rbac"]] = Field(
        default_factory=lambda: ["public"]
    )
    tenant_id: str = Field(..., min_length=1)
    database_mode: Literal["same", "different"] = "same"
    database_name: str | None = None
    fields: list[FieldSpec] = Field(default_factory=list)
    auth: AuthSpec = Field(default_factory=AuthSpec)

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("module_name cannot be empty")
        if " " in value:
            raise ValueError("module_name must not contain spaces")
        if not value.replace("_", "").isalnum():
            raise ValueError("module_name must be alphanumeric with optional underscores")
        if value[0].isdigit():
            raise ValueError("module_name cannot start with a digit")
        return value

    @field_validator("tenant_id")
    @classmethod
    def validate_tenant_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("tenant_id is required")
        return value

    @field_validator("access_modes")
    @classmethod
    def normalize_access_modes(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for item in value:
            item = item.strip().lower()
            if item not in {"public", "auth", "rbac"}:
                raise ValueError(f"Unsupported access mode: {item}")
            if item not in normalized:
                normalized.append(item)

        if not normalized:
            raise ValueError("At least one access mode is required")
        return normalized

    @model_validator(mode="after")
    def normalize_resource(self) -> "ResourceSpec":
        field_names = [field.name for field in self.fields]

        if len(field_names) != len(set(field_names)):
            raise ValueError("Duplicate field names are not allowed")

        clashes = RESERVED_FIELD_NAMES.intersection(field_names)
        if clashes:
            raise ValueError(f"Reserved field names are not allowed: {sorted(clashes)}")

        if "auth" in self.access_modes or "rbac" in self.access_modes:
            self.auth.enabled = True
            self.auth.token_required = True
        else:
            self.auth.enabled = False
            self.auth.token_required = False

        return self

    @property
    def template_keys(self) -> list[str]:
        keys: list[str] = []
        if "public" in self.access_modes:
            keys.append("public_crud_api")
        if "auth" in self.access_modes:
            keys.append("protected_crud_api")
        if "rbac" in self.access_modes:
            keys.append("protected_rbac_api")
        return keys

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResourceSpec":
        return cls.model_validate(data)


class DeleteSpec(BaseModel):
    module_name: str = Field(..., min_length=1)

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("module_name cannot be empty")
        return value


def build_resource_spec(data: dict[str, Any] | ResourceSpec) -> ResourceSpec:
    if isinstance(data, ResourceSpec):
        return data
    return ResourceSpec.model_validate(data)


def build_delete_spec(data: dict[str, Any] | DeleteSpec) -> DeleteSpec:
    if isinstance(data, DeleteSpec):
        return data
    return DeleteSpec.model_validate(data)