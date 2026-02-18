#!/usr/bin/env python3
"""Check ToolForest docs consistency against current source of truth."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"
META_TAXONOMY = ROOT / "docs" / "meta" / "taxonomy.yaml"
MODULES_INDEX = ROOT / "artifacts" / "index" / "modules.json"
TOOL_FOREST_DOC = ROOT / "docs" / "ToolForest.md"
TOOL_FOREST_HTML = ROOT / "docs" / "ToolForestInteractive.html"


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
                if section == "nodes" and current is not None:
                    result.setdefault("nodes", []).append(current)
                    current = None
                section = s[:-1]
                if section not in result:
                    result[section] = [] if section == "nodes" else {}
                continue
            if section == "nodes":
                if s.startswith("- "):
                    if current is not None:
                        result["nodes"].append(current)
                    current = {}
                    tail = s[2:].strip()
                    if ":" in tail:
                        k, v = tail.split(":", 1)
                        current[k.strip()] = v.strip().strip('"').strip("'")
                    continue
                if current is not None and ":" in s:
                    k, v = s.split(":", 1)
                    current[k.strip()] = v.strip().strip('"').strip("'")
    if section == "nodes" and current is not None:
        result.setdefault("nodes", []).append(current)
    return result


def source_from_meta_index(errors: list[str]) -> tuple[list[str], list[str]] | None:
    if not (META_TAXONOMY.exists() and MODULES_INDEX.exists()):
        return None
    taxonomy = parse_simple_yaml(META_TAXONOMY)
    nodes = taxonomy.get("nodes", [])
    if not isinstance(nodes, list) or not nodes:
        errors.append("docs/meta/taxonomy.yaml: invalid nodes")
        return None
    node_ids = [str(n.get("id")) for n in nodes if isinstance(n, dict) and n.get("id")]
    try:
        modules_payload = json.loads(MODULES_INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        errors.append(f"artifacts/index/modules.json invalid JSON: {err}")
        return None
    mods = modules_payload.get("modules", [])
    modules = [
        str(m.get("module"))
        for m in mods
        if isinstance(m, dict) and isinstance(m.get("module"), str)
    ]
    return node_ids, modules


def source_from_registry(errors: list[str]) -> tuple[list[str], list[str]]:
    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        errors.append(f"docs/ssot/registry.json invalid JSON: {err}")
        return [], []
    node_ids = [
        str(n.get("node_id"))
        for n in data.get("taxonomy_nodes", [])
        if isinstance(n, dict) and n.get("node_id")
    ]
    modules = [
        str(m.get("module_path"))
        for m in data.get("modules", [])
        if isinstance(m, dict) and m.get("module_path")
    ]
    modules += [
        str(m.get("module_path"))
        for m in data.get("planned_modules", [])
        if isinstance(m, dict) and m.get("module_path")
    ]
    return node_ids, modules


def require_markers(text: str, markers: list[str], label: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{label} missing required marker: {marker}")


def main() -> int:
    errors: list[str] = []
    source = source_from_meta_index(errors)
    if source is None:
        source = source_from_registry(errors)
    expected_nodes, expected_modules = source

    if not TOOL_FOREST_DOC.exists():
        errors.append("docs/ToolForest.md missing")
    if not TOOL_FOREST_HTML.exists():
        errors.append("docs/ToolForestInteractive.html missing")
    if errors:
        print("[check_tool_forest_consistency] failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    doc = TOOL_FOREST_DOC.read_text(encoding="utf-8")
    html = TOOL_FOREST_HTML.read_text(encoding="utf-8")

    require_markers(
        doc,
        [
            "## view A:Taxonomy main tree",
            "## surface 1:taxonomy Node overview",
            "## surface 4:Entry module",
            "## interactive page(Full details)",
        ],
        "ToolForest.md",
        errors,
    )
    require_markers(
        html,
        ['id="tool-forest-data"', "const MAX_ROWS = 120;"],
        "ToolForestInteractive.html",
        errors,
    )

    for nid in expected_nodes:
        if nid not in doc:
            errors.append(f"ToolForest.md missing taxonomy node `{nid}`")
        if nid not in html:
            errors.append(f"ToolForestInteractive.html missing taxonomy node `{nid}`")
    for module in expected_modules:
        if module not in html:
            errors.append(f"ToolForestInteractive.html missing module `{module}`")

    if errors:
        print("[check_tool_forest_consistency] failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("[check_tool_forest_consistency] passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
