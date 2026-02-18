#!/usr/bin/env python3
"""Sync docs/ssot/registry.json `modules` as a legacy mirror of artifacts/index/modules.json.

This script completes the Phase-2 downgrade path:
- real module discovery source of truth = artifacts/index/modules.json
- registry.modules = compatibility mirror (auto-synced, not manually curated)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"
MODULES_INDEX = ROOT / "artifacts" / "index" / "modules.json"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _layer_to_node(module_path: str, layer: str) -> str:
    if ".Compat" in module_path:
        return "architecture"
    if module_path.startswith("MLTheory.Core.Probability"):
        return "probability"
    if module_path.startswith("MLTheory.Core.Statistics"):
        return "statistics"
    if module_path.startswith("MLTheory.Core.Learning") or module_path.startswith("MLTheory.Methods.Learning"):
        return "learning"
    if module_path.startswith("MLTheory.Methods.OR"):
        return "or"
    if module_path.startswith("MLTheory.Methods.OCO"):
        return "oco"
    if module_path.startswith("MLTheory.Methods.Bandits"):
        return "bandits"
    if module_path.startswith("MLTheory.Core.RL") or module_path.startswith("MLTheory.Methods.RL"):
        return "rl"
    if module_path.startswith("MLTheory.Applications.AI"):
        return "ai"
    if module_path.startswith("MLTheory.Applications.LLM"):
        return "llm"
    if module_path.startswith("MLTheory.Books."):
        if ".FoML2" in module_path:
            return "learning"
        if ".SuttonBartoRL2" in module_path:
            return "rl"
        return "support_infrastructure"
    if module_path == "MLTheory.Core":
        return "foundations"
    if module_path == "MLTheory.Methods":
        return "methods_problems"
    if module_path.startswith("MLTheory.Applications."):
        return "applications_systems"
    if layer == "books":
        return "support_infrastructure"
    return "ml_root"


def _default_module_row(module_path: str, layer: str) -> dict[str, Any]:
    layer_norm = layer if layer in {"core", "methods", "applications", "books", "legacy"} else "legacy"
    role = "compat" if ".Compat" in module_path else "tool"
    user_surface = "internal" if role == "compat" else "public"
    source_track = "books" if layer_norm == "books" else "native"
    return {
        "module_path": module_path,
        "primary_node_id": _layer_to_node(module_path, layer_norm),
        "source_track": source_track,
        "status": "partial",
        "source": "mathlib",
        "book_refs": [],
        "layer": layer_norm,
        "proof_status": "statement",
        "placeholder_policy_scope": "forbidden" if layer_norm in {"core", "methods"} else "allowed",
        "role": role,
        "user_surface": user_surface,
        "formal_decl_refs": [],
    }


def _merge_row(legacy: dict[str, Any] | None, module_path: str, layer: str) -> dict[str, Any]:
    if legacy is None:
        return _default_module_row(module_path, layer)

    row = dict(legacy)
    defaults = _default_module_row(module_path, layer)
    for key, value in defaults.items():
        row.setdefault(key, value)

    # Source of module identity always follows auto-discovered index.
    row["module_path"] = module_path
    if layer in {"core", "methods", "applications", "books", "legacy"}:
        row["layer"] = layer
    else:
        row["layer"] = row.get("layer", "legacy")

    # Keep placeholder policy coherent with layer hard gate.
    if row["layer"] in {"core", "methods"}:
        row["placeholder_policy_scope"] = "forbidden"

    return row


def build_expected_modules(registry: dict[str, Any], modules_index: dict[str, Any]) -> list[dict[str, Any]]:
    legacy_rows = registry.get("modules", [])
    legacy_map: dict[str, dict[str, Any]] = {}
    if isinstance(legacy_rows, list):
        for row in legacy_rows:
            if isinstance(row, dict):
                module_path = row.get("module_path")
                if isinstance(module_path, str):
                    legacy_map[module_path] = row

    expected: dict[str, dict[str, Any]] = {}

    # 1) Index-discovered modules (authoritative set for real modules).
    for row in modules_index.get("modules", []):
        if not isinstance(row, dict):
            continue
        if row.get("package") != "MLTheory":
            continue
        module_path = row.get("module")
        layer = row.get("layer", "legacy")
        if not isinstance(module_path, str) or not module_path.startswith("MLTheory."):
            continue
        expected[module_path] = _merge_row(legacy_map.get(module_path), module_path, str(layer))

    # 2) Keep existing legacy rows that are not covered by index (backward compatibility).
    for module_path, row in legacy_map.items():
        if module_path not in expected:
            expected[module_path] = _merge_row(row, module_path, str(row.get("layer", "legacy")))

    return [expected[k] for k in sorted(expected)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write updated registry modules")
    parser.add_argument("--check", action="store_true", help="fail if registry modules are out of sync")
    args = parser.parse_args()

    registry = _load_json(REGISTRY)
    modules_index = _load_json(MODULES_INDEX)
    expected_modules = build_expected_modules(registry, modules_index)
    current_modules = registry.get("modules", [])

    in_sync = current_modules == expected_modules
    if args.check:
        if in_sync:
            print("[sync_registry_modules_legacy] passed.")
            return 0
        print("[sync_registry_modules_legacy] registry.modules is out of sync with artifacts/index/modules.json")
        print("Run: python3 tools/docs/sync_registry_modules_legacy.py --write")
        return 1

    if args.write:
        registry["modules"] = expected_modules
        meta = registry.setdefault("meta", {})
        if isinstance(meta, dict):
            meta["module_catalog_source"] = "artifacts/index/modules.json"
            meta["module_catalog_mode"] = "legacy_mirror_auto_synced"
        REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(
            f"[sync_registry_modules_legacy] wrote {REGISTRY} "
            f"(modules={len(expected_modules)}, in_sync_before={in_sync})"
        )
        return 0

    print(f"in_sync={in_sync}; use --check or --write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

