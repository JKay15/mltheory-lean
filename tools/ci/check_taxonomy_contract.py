#!/usr/bin/env python3
"""Hard gate for taxonomy v2 structural contract."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"

SOURCE_TRACKS = {"native", "books", "legacy"}
RELATION_TYPES = {"secondary_parent", "related"}

LEGACY_DOMAIN_PATTERNS = [
    re.compile(r"\bIndex\b", re.IGNORECASE),
    re.compile(r"\bTheory\b", re.IGNORECASE),
    re.compile(r"\bRoot\b", re.IGNORECASE),
    re.compile(r"\bOperations\s+Research\b", re.IGNORECASE),
    re.compile(r"\bML\s+Theory\b", re.IGNORECASE),
]


def module_file_path(module_path: str) -> Path:
    if module_path == "MLTheory":
        return ROOT / "MLTheory.lean"
    return ROOT / f"{module_path.replace('.', '/')}.lean"


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    errors: list[str] = []

    nodes = data.get("taxonomy_nodes", [])
    relations = data.get("taxonomy_relations", [])
    modules = data.get("modules", [])
    planned_modules = data.get("planned_modules", [])

    if not isinstance(nodes, list) or not nodes:
        errors.append("taxonomy_nodes missing or empty")
        nodes = []
    if not isinstance(relations, list):
        errors.append("taxonomy_relations must be an array")
        relations = []
    if not isinstance(modules, list):
        errors.append("modules must be an array")
        modules = []
    if not isinstance(planned_modules, list):
        errors.append("planned_modules must be an array")
        planned_modules = []

    node_ids = []
    parent = {}
    for i, node in enumerate(nodes):
        nid = node.get("node_id")
        if not isinstance(nid, str) or not nid:
            errors.append(f"taxonomy_nodes[{i}].node_id is invalid")
            continue
        node_ids.append(nid)
        parent[nid] = node.get("primary_parent_id")
    node_set = set(node_ids)
    if len(node_set) != len(node_ids):
        errors.append("duplicate taxonomy node_id detected")

    roots = [nid for nid in node_ids if parent.get(nid) is None]
    if len(roots) != 1:
        errors.append(f"expected exactly 1 taxonomy root, got {len(roots)}")

    for nid in node_ids:
        p = parent.get(nid)
        if p is not None and p not in node_set:
            errors.append(f"node `{nid}` references missing parent `{p}`")

    # No cycles on primary parent chain.
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(nid: str) -> None:
        if nid in visiting:
            errors.append(f"cycle detected in primary_parent_id chain at `{nid}`")
            return
        if nid in visited:
            return
        visiting.add(nid)
        p = parent.get(nid)
        if isinstance(p, str):
            dfs(p)
        visiting.remove(nid)
        visited.add(nid)

    for nid in node_ids:
        dfs(nid)

    # Reachability from root.
    children: dict[str, list[str]] = defaultdict(list)
    for nid in node_ids:
        p = parent.get(nid)
        if isinstance(p, str):
            children[p].append(nid)
    if roots:
        stack = [roots[0]]
        seen = set()
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(children.get(cur, []))
        unreachable = sorted(node_set - seen)
        if unreachable:
            errors.append(f"unreachable taxonomy nodes from root `{roots[0]}`: {unreachable}")

    # Relation validation.
    seen_rel = set()
    for i, rel in enumerate(relations):
        frm = rel.get("from_node")
        to = rel.get("to_node")
        rtype = rel.get("relation_type")
        strength = rel.get("strength")
        if frm not in node_set:
            errors.append(f"taxonomy_relations[{i}].from_node unknown: {frm}")
        if to not in node_set:
            errors.append(f"taxonomy_relations[{i}].to_node unknown: {to}")
        if rtype not in RELATION_TYPES:
            errors.append(f"taxonomy_relations[{i}].relation_type invalid: {rtype}")
        if not isinstance(strength, (int, float)) or not (0 <= float(strength) <= 1):
            errors.append(f"taxonomy_relations[{i}].strength must be in [0,1]")
        key = (frm, to, rtype)
        if key in seen_rel:
            errors.append(f"duplicate taxonomy relation detected: {key}")
        seen_rel.add(key)

    # Module checks.
    mod_paths = set()
    for i, mod in enumerate(modules):
        mpath = mod.get("module_path")
        nid = mod.get("primary_node_id")
        source_track = mod.get("source_track")
        label = f"modules[{i}]"

        if not isinstance(mpath, str) or not mpath:
            errors.append(f"{label}.module_path invalid")
            continue
        if mpath in mod_paths:
            errors.append(f"{label}.module_path duplicate: {mpath}")
        mod_paths.add(mpath)

        if "domain" in mod:
            errors.append(f"{label} contains retired key `domain`")
        if nid not in node_set:
            errors.append(f"{label}.primary_node_id unknown: {nid}")
        if source_track not in SOURCE_TRACKS:
            errors.append(f"{label}.source_track invalid: {source_track}")
        if not module_file_path(mpath).exists():
            errors.append(f"{label}.module_path is not file-backed: {mpath}")
        for pat in LEGACY_DOMAIN_PATTERNS:
            if pat.search(mpath):
                errors.append(f"{label}.module_path contains legacy domain token: {mpath}")

    # planned_modules checks.
    planned_paths = set()
    for i, mod in enumerate(planned_modules):
        mpath = mod.get("module_path")
        nid = mod.get("target_node_id")
        source_track = mod.get("source_track")
        label = f"planned_modules[{i}]"

        if not isinstance(mpath, str) or not mpath:
            errors.append(f"{label}.module_path invalid")
            continue
        if mpath in planned_paths:
            errors.append(f"{label}.module_path duplicate: {mpath}")
        planned_paths.add(mpath)
        if mpath in mod_paths:
            errors.append(f"{label}.module_path duplicated in modules: {mpath}")

        if nid not in node_set:
            errors.append(f"{label}.target_node_id unknown: {nid}")
        if source_track not in SOURCE_TRACKS:
            errors.append(f"{label}.source_track invalid: {source_track}")

    # Canonical spec boundary in MLTheory.
    for i, spec in enumerate(data.get("canonical_specs", [])):
        if spec.get("repo") != "MLTheory":
            errors.append(f"canonical_specs[{i}].repo must be MLTheory")

    if errors:
        print("[check_taxonomy_contract] failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("[check_taxonomy_contract] passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
