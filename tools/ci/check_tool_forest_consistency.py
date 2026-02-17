#!/usr/bin/env python3
"""Check taxonomy/tool-forest consistency from SSOT."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"
TOOL_FOREST_DOC = ROOT / "docs" / "ToolForest.md"
TOOL_FOREST_HTML = ROOT / "docs" / "ToolForestInteractive.html"


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    nodes = data.get("taxonomy_nodes", [])
    relations = data.get("taxonomy_relations", [])
    modules = data.get("modules", [])
    planned_modules = data.get("planned_modules", [])
    errors: list[str] = []

    if not nodes:
        errors.append("taxonomy_nodes is empty")
    node_ids = [n.get("node_id") for n in nodes]
    if len(node_ids) != len(set(node_ids)):
        errors.append("duplicate node_id detected")

    node_map = {n["node_id"]: n for n in nodes if "node_id" in n}
    children = defaultdict(list)
    roots = []
    for n in nodes:
        nid = n.get("node_id")
        parent = n.get("primary_parent_id")
        if not nid:
            errors.append("taxonomy node with empty node_id")
            continue
        if parent:
            if parent not in node_map:
                errors.append(f"node `{nid}` references missing parent `{parent}`")
            else:
                children[parent].append(nid)
        else:
            roots.append(nid)

    if len(roots) != 1:
        errors.append(f"expected exactly one root node, got {len(roots)}")

    # Cycle detection on primary parent tree.
    visited = set()
    stack = set()

    def dfs(node: str) -> None:
        if node in stack:
            errors.append(f"cycle detected at node `{node}`")
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for nxt in children.get(node, []):
            dfs(nxt)
        stack.remove(node)

    for r in roots:
        dfs(r)

    # Relation endpoints.
    for i, rel in enumerate(relations):
        frm = rel.get("from_node")
        to = rel.get("to_node")
        if frm not in node_map:
            errors.append(f"taxonomy_relations[{i}].from_node unknown: {frm}")
        if to not in node_map:
            errors.append(f"taxonomy_relations[{i}].to_node unknown: {to}")

    # Module references.
    for i, mod in enumerate(modules):
        nid = mod.get("primary_node_id")
        path = mod.get("module_path", f"<modules[{i}]>")
        if not nid:
            errors.append(f"{path}: missing primary_node_id")
        elif nid not in node_map:
            errors.append(f"{path}: primary_node_id `{nid}` not found")

    for i, mod in enumerate(planned_modules):
        nid = mod.get("target_node_id")
        path = mod.get("module_path", f"<planned_modules[{i}]>")
        if not nid:
            errors.append(f"{path}: missing target_node_id")
        elif nid not in node_map:
            errors.append(f"{path}: target_node_id `{nid}` not found")

    # Ensure generated markdown doc contains required sections.
    if TOOL_FOREST_DOC.exists():
        doc = TOOL_FOREST_DOC.read_text(encoding="utf-8")
        required_markers = [
            "## 视图 A：Taxonomy 主树",
            "## 表 1：taxonomy 节点总览",
            "## 表 2：关系边（次父/关联）",
            "## 表 3：source_track 分布（真实/规划）",
            "## 表 4：入口模块（canonical + tool",
            "## 表 5：规划模块样例（Top",
            "## 交互页（完整明细）",
            "## 使用说明（人 + Codex）",
        ]
        for marker in required_markers:
            if marker not in doc:
                errors.append(f"ToolForest.md missing required section `{marker}`")
        for nid in node_map:
            if nid not in doc:
                errors.append(f"ToolForest.md missing taxonomy node label `{nid}`")
    else:
        errors.append("docs/ToolForest.md missing")

    # Ensure interactive html exists and carries payload with nodes+modules.
    if TOOL_FOREST_HTML.exists():
        html = TOOL_FOREST_HTML.read_text(encoding="utf-8")
        if 'id="tool-forest-data"' not in html:
            errors.append("ToolForestInteractive.html missing embedded data payload marker")
        for nid in node_map:
            if nid not in html:
                errors.append(f"ToolForestInteractive.html missing node `{nid}`")
        for mod in modules:
            mp = mod.get("module_path")
            if mp and mp not in html:
                errors.append(f"ToolForestInteractive.html missing real module `{mp}`")
        for mod in planned_modules:
            mp = mod.get("module_path")
            if mp and mp not in html:
                errors.append(f"ToolForestInteractive.html missing planned module `{mp}`")
    else:
        errors.append("docs/ToolForestInteractive.html missing")

    if errors:
        print("[check_tool_forest_consistency] failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("[check_tool_forest_consistency] passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
