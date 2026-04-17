from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from mini_agent.registry import CORE_FILES, TEMPLATE_REGISTRY


def scan_supported_templates() -> Dict[str, Dict[str, object]]:
    return {key: value.copy() for key, value in TEMPLATE_REGISTRY.items()}


def scan_generated_layout(template_key: str) -> Dict[str, List[str]]:
    template = TEMPLATE_REGISTRY.get(template_key)
    if not template:
        raise ValueError(f"Unknown template_key: {template_key}")

    return {
        "core_files": CORE_FILES.copy() if template.get("requires_core") else [],
        "module_files": list(template.get("module_files", [])),
    }


def list_generated_modules(output_dir: str) -> List[str]:
    root = Path(output_dir)
    if not root.exists():
        return []

    modules: List[str] = []
    for child in root.iterdir():
        if child.is_dir() and child.name not in {"core", "__pycache__"}:
            modules.append(child.name)
    return sorted(modules)


def inspect_module_files(output_dir: str, module_name: str) -> Dict[str, object]:
    module_dir = Path(output_dir) / module_name
    if not module_dir.exists():
        return {"exists": False, "files": [], "missing": []}

    files = sorted([p.name for p in module_dir.iterdir() if p.is_file()])
    return {"exists": True, "files": files, "missing": []}