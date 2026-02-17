#!/usr/bin/env python3
"""Gate for namespace/path layout convergence after taxonomy v2 stabilization."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"

PREFIX_BY_LAYER = {
    "core": "MLTheory.Core",
    "methods": "MLTheory.Methods",
    "applications": "MLTheory.Applications",
    "books": "MLTheory.Books",
}

# Planned modules are future canonical modules; they must already live on
# stable layered prefixes (not legacy top-level roots).
PLANNED_PREFIX_BY_TARGET_NODE = {
    "probability": "MLTheory.Core.Probability",
    "statistics": "MLTheory.Core.Statistics",
    "learning": "MLTheory.Methods.Learning",
    "or": "MLTheory.Methods.OR",
    "oco": "MLTheory.Methods.OCO",
    "bandits": "MLTheory.Methods.Bandits",
    "rl": "MLTheory.Methods.RL",
    "ai": "MLTheory.Applications.AI",
    "llm": "MLTheory.Applications.LLM",
}


def _matches_prefix(module_path: str, prefix: str) -> bool:
    return module_path == prefix or module_path.startswith(prefix + ".")


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    modules = data.get("modules", [])
    planned = data.get("planned_modules", [])
    aliases = data.get("aliases", [])
    cleanup = data.get("structure_cleanup_candidates", [])

    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(modules, list):
        errors.append("modules must be an array")
        modules = []
    if not isinstance(planned, list):
        errors.append("planned_modules must be an array")
        planned = []
    if not isinstance(aliases, list):
        errors.append("aliases must be an array")
        aliases = []
    if not isinstance(cleanup, list):
        errors.append("structure_cleanup_candidates must be an array")
        cleanup = []

    module_paths = {
        m.get("module_path")
        for m in modules
        if isinstance(m, dict) and isinstance(m.get("module_path"), str)
    }
    planned_paths = {
        m.get("module_path")
        for m in planned
        if isinstance(m, dict) and isinstance(m.get("module_path"), str)
    }
    known_targets = module_paths | planned_paths

    cleanup_paths = {
        c.get("module_path")
        for c in cleanup
        if isinstance(c, dict) and isinstance(c.get("module_path"), str)
    }

    for i, m in enumerate(modules):
        if not isinstance(m, dict):
            errors.append(f"modules[{i}] must be an object")
            continue
        label = f"modules[{i}]"
        module_path = m.get("module_path")
        layer = m.get("layer")
        source_track = m.get("source_track")
        role = m.get("role")

        if not isinstance(module_path, str):
            errors.append(f"{label}.module_path must be string")
            continue
        if not isinstance(layer, str):
            errors.append(f"{label}.layer must be string")
            continue

        if layer in PREFIX_BY_LAYER:
            prefix = PREFIX_BY_LAYER[layer]
            if not _matches_prefix(module_path, prefix):
                errors.append(
                    f"{label}: layer={layer} requires prefix `{prefix}` but got `{module_path}`"
                )
        elif layer == "legacy":
            # Legacy compatibility modules are intentionally restricted to top-level paths,
            # e.g. MLTheory.Probability / MLTheory.Optimization.
            if module_path != "MLTheory" and module_path.count(".") != 1:
                errors.append(
                    f"{label}: legacy layer must stay top-level (`MLTheory.X`), got `{module_path}`"
                )
            for prefix in PREFIX_BY_LAYER.values():
                if _matches_prefix(module_path, prefix):
                    errors.append(
                        f"{label}: legacy layer must not live under layered prefix `{prefix}`"
                    )
        else:
            errors.append(f"{label}: unknown layer `{layer}`")

        if layer == "books" and source_track != "books":
            errors.append(f"{label}: books layer must use source_track=books")
        if layer in {"core", "methods", "applications"} and source_track != "native":
            errors.append(f"{label}: {layer} layer must use source_track=native")
        if layer == "legacy" and role not in {"compat", "bridge"}:
            warnings.append(
                f"{label}: legacy layer usually uses role=compat/bridge, got role={role}"
            )

    for i, m in enumerate(planned):
        if not isinstance(m, dict):
            errors.append(f"planned_modules[{i}] must be an object")
            continue
        label = f"planned_modules[{i}]"
        module_path = m.get("module_path")
        source_track = m.get("source_track")
        target_node = m.get("target_node_id")

        if not isinstance(module_path, str) or not module_path:
            errors.append(f"{label}.module_path must be non-empty string")
            continue
        if source_track == "books":
            if not _matches_prefix(module_path, PREFIX_BY_LAYER["books"]):
                errors.append(
                    f"{label}: source_track=books requires prefix `{PREFIX_BY_LAYER['books']}`, got `{module_path}`"
                )
            continue
        if source_track == "legacy":
            errors.append(
                f"{label}: source_track=legacy is no longer allowed for planned_modules; migrate to canonical native path"
            )
            continue
        if source_track != "native":
            errors.append(f"{label}: unsupported source_track `{source_track}`")
            continue

        if not isinstance(target_node, str) or not target_node:
            errors.append(f"{label}.target_node_id must be non-empty string")
            continue
        expected_prefix = PLANNED_PREFIX_BY_TARGET_NODE.get(target_node)
        if expected_prefix is None:
            warnings.append(
                f"{label}: no strict planned prefix rule for target_node={target_node}"
            )
            continue
        if not _matches_prefix(module_path, expected_prefix):
            errors.append(
                f"{label}: target_node={target_node} expects prefix `{expected_prefix}`, got `{module_path}`"
            )

    for i, a in enumerate(aliases):
        if not isinstance(a, dict):
            errors.append(f"aliases[{i}] must be an object")
            continue
        label = f"aliases[{i}]"
        legacy = a.get("legacy_module")
        canonical = a.get("canonical_module")
        status = a.get("status")

        if not isinstance(legacy, str) or not legacy:
            errors.append(f"{label}.legacy_module must be non-empty string")
            continue
        if not isinstance(canonical, str) or not canonical:
            errors.append(f"{label}.canonical_module must be non-empty string")
            continue

        if canonical not in known_targets:
            errors.append(
                f"{label}: canonical_module `{canonical}` not found in modules/planned_modules"
            )

        legacy_exists = legacy in module_paths
        if status == "active":
            if not legacy_exists:
                errors.append(
                    f"{label}: active alias expects existing legacy module `{legacy}` in modules"
                )
        elif status == "deprecated":
            if legacy_exists and legacy not in cleanup_paths:
                errors.append(
                    f"{label}: deprecated legacy module `{legacy}` still exists but is not tracked by structure_cleanup_candidates"
                )
        else:
            errors.append(f"{label}: invalid status `{status}`")

    if errors:
        print("[check_namespace_layout] failed:")
        for err in errors:
            print(f"- {err}")
        if warnings:
            print("[check_namespace_layout] warnings:")
            for w in warnings:
                print(f"  * {w}")
        return 1

    print(
        "[check_namespace_layout] passed: "
        f"modules={len(module_paths)}, planned_modules={len(planned_paths)}, aliases={len(aliases)}"
    )
    if warnings:
        print("[check_namespace_layout] warnings:")
        for w in warnings:
            print(f"  * {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
