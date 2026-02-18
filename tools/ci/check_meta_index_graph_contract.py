#!/usr/bin/env python3
"""Validate meta/index/graph artifact contracts for vNext workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def parse_simple_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    result: dict = {}
    section: str | None = None
    current: dict | None = None
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            s = line.strip()
            if indent == 0 and s.endswith(":"):
                if section in {"nodes", "bindings"} and current is not None:
                    result.setdefault(section, []).append(current)
                    current = None
                section = s[:-1]
                if section not in result:
                    result[section] = [] if section in {"nodes", "bindings", "canonical_modules", "canonical_decls"} else {}
                continue
            if section in {"nodes", "bindings"}:
                if s.startswith("- "):
                    if current is not None:
                        result[section].append(current)
                    current = {}
                    tail = s[2:].strip()
                    if ":" in tail:
                        k, v = tail.split(":", 1)
                        current[k.strip()] = v.strip().strip('"').strip("'")
                    continue
                if current is not None and ":" in s:
                    k, v = s.split(":", 1)
                    current[k.strip()] = v.strip().strip('"').strip("'")
                continue
            if section in {"canonical_modules", "canonical_decls"} and s.startswith("- "):
                result[section].append(s[2:].strip().strip('"').strip("'"))
                continue

            if section is not None and isinstance(result.get(section), dict):
                if ":" in s:
                    k, v = s.split(":", 1)
                    key = k.strip()
                    val = v.strip()
                    if val == "":
                        result[section][key] = []
                    else:
                        result[section][key] = val.strip('"').strip("'")
                elif s.startswith("- "):
                    keys = list(result[section].keys())
                    if keys:
                        result[section][keys[-1]].append(s[2:].strip().strip('"').strip("'"))
    if section in {"nodes", "bindings"} and current is not None:
        result.setdefault(section, []).append(current)
    return result


def load_json(path: Path, errors: list[str]) -> dict | None:
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(ROOT)}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            errors.append(f"{path.relative_to(ROOT)}: root must be object")
            return None
        return data
    except json.JSONDecodeError as err:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {err}")
        return None


def require_keys(obj: dict, keys: list[str], label: str, errors: list[str]) -> None:
    for key in keys:
        if key not in obj:
            errors.append(f"{label}: missing key `{key}`")


def validate_meta(errors: list[str]) -> None:
    taxonomy = parse_simple_yaml(ROOT / "docs" / "meta" / "taxonomy.yaml")
    aliases = parse_simple_yaml(ROOT / "docs" / "meta" / "aliases.yaml")
    canon = parse_simple_yaml(ROOT / "docs" / "meta" / "canon.yaml")

    nodes = taxonomy.get("nodes", [])
    if not isinstance(nodes, list) or not nodes:
        errors.append("docs/meta/taxonomy.yaml: `nodes` must be non-empty list")
    else:
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                errors.append(f"taxonomy.nodes[{i}] must be object")
                continue
            if not node.get("id") or not node.get("title"):
                errors.append(f"taxonomy.nodes[{i}] missing id/title")

    aliases_map = aliases.get("aliases")
    if not isinstance(aliases_map, dict):
        errors.append("docs/meta/aliases.yaml: missing mapping `aliases`")

    canon_mods = canon.get("canonical_modules")
    if not isinstance(canon_mods, list):
        errors.append("docs/meta/canon.yaml: `canonical_modules` must be list")


def validate_artifacts(errors: list[str]) -> None:
    modules = load_json(ROOT / "artifacts" / "index" / "modules.json", errors)
    imports = load_json(ROOT / "artifacts" / "index" / "imports.json", errors)
    decls = load_json(ROOT / "artifacts" / "index" / "decls.json", errors)
    module_graph = load_json(ROOT / "artifacts" / "graphs" / "module_graph.json", errors)
    decl_graph = load_json(ROOT / "artifacts" / "graphs" / "decl_graph.json", errors)
    subgraph = load_json(ROOT / "artifacts" / "graphs" / "subgraph.json", errors)
    usage_graph = load_json(ROOT / "artifacts" / "graphs" / "usage_graph.json", errors)
    usage_suggestions = load_json(ROOT / "artifacts" / "index" / "usage_suggestions.json", errors)

    if modules is not None:
        require_keys(modules, ["generated_at", "modules"], "modules.json", errors)
        if not isinstance(modules.get("modules"), list):
            errors.append("modules.json: `modules` must be list")

    if imports is not None:
        require_keys(imports, ["generated_at", "nodes", "edges"], "imports.json", errors)
        if not isinstance(imports.get("edges"), list):
            errors.append("imports.json: `edges` must be list")

    if decls is not None:
        require_keys(decls, ["generated_at", "decls"], "decls.json", errors)
        if not isinstance(decls.get("decls"), list):
            errors.append("decls.json: `decls` must be list")

    if module_graph is not None:
        require_keys(module_graph, ["generated_at", "nodes", "edges"], "module_graph.json", errors)

    if decl_graph is not None:
        require_keys(decl_graph, ["nodes", "edges"], "decl_graph.json", errors)

    allowed_edge_types = {
        "imports",
        "decl_in_module",
        "uses_type",
        "uses_value",
        "binds",
        "alias_of",
        "used_recently",
    }
    if subgraph is not None:
        require_keys(subgraph, ["generated_at", "nodes", "edges"], "subgraph.json", errors)
        for i, edge in enumerate(subgraph.get("edges", [])):
            if not isinstance(edge, dict):
                errors.append(f"subgraph.json: edges[{i}] must be object")
                continue
            etype = edge.get("type")
            if etype not in allowed_edge_types:
                errors.append(f"subgraph.json: edges[{i}].type invalid: {etype}")

    if usage_graph is not None:
        require_keys(usage_graph, ["generated_at", "nodes", "edges"], "usage_graph.json", errors)

    if usage_suggestions is not None:
        require_keys(
            usage_suggestions,
            ["generated_at", "spine_candidates", "entry_module_candidates"],
            "usage_suggestions.json",
            errors,
        )


def main() -> int:
    errors: list[str] = []
    validate_meta(errors)
    validate_artifacts(errors)
    if errors:
        print("[check_meta_index_graph_contract] failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("[check_meta_index_graph_contract] passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
