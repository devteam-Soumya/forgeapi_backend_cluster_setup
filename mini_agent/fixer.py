from __future__ import annotations

from mini_agent.registry import TEMPLATE_REGISTRY
from mini_agent.spec import ModuleSpec


def rectify_spec(spec):
    if isinstance(spec, dict):
        spec = ModuleSpec.from_dict(spec)

    template = TEMPLATE_REGISTRY.get(spec.template_key)
    if not template:
        raise ValueError(f"Unsupported template_key: {spec.template_key}")

    auth_required = bool(template.get("auth_required", False))
    signup_enabled = bool(template.get("signup_enabled", False))
    login_enabled = bool(template.get("login_enabled", False))
    token_required = bool(template.get("token_required", False))

    spec.auth.enabled = auth_required
    spec.auth.signup_enabled = signup_enabled
    spec.auth.login_enabled = login_enabled
    spec.auth.token_required = token_required

    if spec.template_key == "public_api":
        spec.auth.enabled = False
        spec.auth.signup_enabled = False
        spec.auth.login_enabled = False
        spec.auth.token_required = False

    if spec.template_key == "auth_basic":
        spec.fields = []
        spec.route_prefix = "/auth"

    if not spec.route_prefix.startswith("/"):
        spec.route_prefix = f"/{spec.route_prefix}"

    if not spec.tags:
        spec.tags = [spec.module_name]

    return spec