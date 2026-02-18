#!/usr/bin/env python3
"""Generate merged subgraph artifact from module/decl/usage/meta layers."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_scalar(raw: str):
    text = raw.strip()
    if text == "null":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if text.isdigit():
        return int(text)
    return text.strip('"').strip("'")


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
            stripped = line.strip()

            if indent == 0 and stripped.endswith(":"):
                if section in {"nodes", "bindings"} and current is not None:
                    result.setdefault(section, []).append(current)
                    current = None
                section = stripped[:-1]
                if section not in result:
                    if section in {"nodes", "bindings"}:
                        result[section] = []
                    else:
                        result[section] = {}
                continue

            if section in {"nodes", "bindings"}:
                if stripped.startswith("- "):
                    if current is not None:
                        result[section].append(current)
                    current = {}
                    tail = stripped[2:].strip()
                    if ":" in tail:
                        k, v = tail.split(":", 1)
                        current[k.strip()] = parse_scalar(v)
                    continue
                if current is not None and ":" in stripped:
                    k, v = stripped.split(":", 1)
                    current[k.strip()] = parse_scalar(v)
                continue

            if section is not None and isinstance(result.get(section), dict) and ":" in stripped:
                k, v = stripped.split(":", 1)
                key = k.strip()
                val = v.strip()
                if val == "":
                    result[section][key] = []
                else:
                    result[section][key] = parse_scalar(val)
                continue

            if section is not None and isinstance(result.get(section), dict) and stripped.startswith("- "):
                val = parse_scalar(stripped[2:])
                # Append to the latest key of this mapping section.
                keys = list(result[section].keys())
                if keys:
                    result[section][keys[-1]].append(val)

    if section in {"nodes", "bindings"} and current is not None:
        result.setdefault(section, []).append(current)
    return result


def load_canon(path: Path) -> tuple[set[str], set[str]]:
    data = parse_simple_yaml(path)
    mods = set()
    decls = set()
    for v in data.get("canonical_modules", []):
        if isinstance(v, str):
            mods.add(v)
    for v in data.get("canonical_decls", []):
        if isinstance(v, str):
            decls.add(v)
    return mods, decls


def layer_from_module(module: str) -> str:
    if module.startswith("MLTheory.Core."):
        return "core"
    if module.startswith("MLTheory.Methods."):
        return "methods"
    if module.startswith("MLTheory.Applications."):
        return "applications"
    if module.startswith("MLTheory.Books."):
        return "books"
    if module.startswith("Mathlib."):
        return "mathlib"
    return "other"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module-graph", type=Path, required=True, help="module_graph.json path")
    ap.add_argument("--decl-graph", type=Path, required=True, help="decl_graph.json path")
    ap.add_argument("--usage-graph", type=Path, required=True, help="usage_graph.json path")
    ap.add_argument("--modules", type=Path, required=True, help="modules.json path")
    ap.add_argument("--taxonomy", type=Path, required=True, help="docs/meta/taxonomy.yaml path")
    ap.add_argument("--canon", type=Path, required=True, help="docs/meta/canon.yaml path")
    ap.add_argument(
        "--mathlib-slice",
        type=Path,
        default=Path("artifacts/index/mathlib_slice.json"),
        help="mathlib_slice.json path",
    )
    ap.add_argument(
        "--mathlib-imports",
        type=Path,
        default=Path("artifacts/index/mathlib_imports.json"),
        help="mathlib_imports.json path",
    )
    ap.add_argument(
        "--mathlib-hubs",
        type=Path,
        default=Path("artifacts/index/mathlib_hubs.json"),
        help="mathlib_hubs.json path",
    )
    ap.add_argument(
        "--mathlib-aggregators",
        type=Path,
        default=Path("artifacts/index/mathlib_aggregators.json"),
        help="mathlib_aggregators.json path",
    )
    ap.add_argument(
        "--mltheory-to-mathlib",
        type=Path,
        default=Path("artifacts/index/mltheory_to_mathlib.json"),
        help="mltheory_to_mathlib.json path",
    )
    ap.add_argument(
        "--max-mathlib-modules",
        type=int,
        default=220,
        help="max number of mathlib module nodes injected into subgraph",
    )
    ap.add_argument("--out", type=Path, required=True, help="subgraph.json output path")
    ap.add_argument(
        "--export-docs-data",
        type=Path,
        default=Path("docs/_auto/subgraph.json"),
        help="optional docs/_auto subgraph copy",
    )
    args = ap.parse_args()

    module_graph = load_json(args.module_graph.resolve())
    decl_graph = load_json(args.decl_graph.resolve())
    usage_graph = load_json(args.usage_graph.resolve())
    modules = load_json(args.modules.resolve())
    taxonomy = parse_simple_yaml(args.taxonomy.resolve())
    canon_modules, canon_decls = load_canon(args.canon.resolve())

    def load_optional(path: Path) -> dict:
        p = path.resolve()
        if not p.exists():
            return {}
        try:
            data = load_json(p)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

    mathlib_slice = load_optional(args.mathlib_slice)
    mathlib_imports = load_optional(args.mathlib_imports)
    mathlib_hubs = load_optional(args.mathlib_hubs)
    mathlib_aggregators = load_optional(args.mathlib_aggregators)
    mltheory_to_mathlib = load_optional(args.mltheory_to_mathlib)

    module_to_path = {}
    module_to_layer = {}
    for row in modules.get("modules", []):
        if not isinstance(row, dict):
            continue
        module = row.get("module")
        if not isinstance(module, str):
            continue
        module_to_path[module] = row.get("path", "")
        module_to_layer[module] = row.get("layer", layer_from_module(module))

    usage_top = {
        n.get("id")
        for n in usage_graph.get("nodes", [])[:80]
        if isinstance(n, dict) and isinstance(n.get("id"), str)
    }

    nodes: list[dict] = []
    seen_nodes: set[str] = set()

    for row in module_graph.get("nodes", []):
        if not isinstance(row, dict):
            continue
        module_id = row.get("id")
        if not isinstance(module_id, str):
            continue
        if module_id in seen_nodes:
            continue
        seen_nodes.add(module_id)
        nodes.append(
            {
                "id": module_id,
                "kind": "module",
                "title": row.get("title", module_id),
                "layer": module_to_layer.get(module_id, row.get("layer", "other")),
                "spine": module_id in canon_modules,
                "path": module_to_path.get(module_id, ""),
                "package": "mathlib" if module_id.startswith("Mathlib.") else "MLTheory",
            }
        )

    max_mathlib = max(0, int(args.max_mathlib_modules))
    selected_mathlib: set[str] = set()
    roots = [m for m in mathlib_slice.get("root_direct_imports", []) if isinstance(m, str)]
    selected_mathlib.update(m for m in roots if m.startswith("Mathlib"))

    agg_modules = [
        r.get("module")
        for r in mathlib_aggregators.get("aggregators", [])
        if isinstance(r, dict) and isinstance(r.get("module"), str)
    ]
    hub_modules = [
        r.get("module")
        for r in mathlib_hubs.get("top_by_fan_in", []) + mathlib_hubs.get("top_by_fan_out", [])
        if isinstance(r, dict) and isinstance(r.get("module"), str)
    ]
    selected_mathlib.update(m for m in agg_modules[:80] if m.startswith("Mathlib"))
    selected_mathlib.update(m for m in hub_modules[:120] if m.startswith("Mathlib"))

    slice_modules = [m for m in mathlib_slice.get("slice", []) if isinstance(m, str)]
    slice_modules = [m for m in slice_modules if m.startswith("Mathlib")]
    for m in slice_modules:
        if len(selected_mathlib) >= max_mathlib:
            break
        selected_mathlib.add(m)

    agg_set = set(m for m in agg_modules if isinstance(m, str))
    root_set = set(roots)
    for module_id in sorted(selected_mathlib):
        if module_id in seen_nodes:
            continue
        seen_nodes.add(module_id)
        nodes.append(
            {
                "id": module_id,
                "kind": "module",
                "title": module_id,
                "layer": "mathlib",
                "spine": module_id in agg_set or module_id in root_set,
                "path": "",
                "package": "mathlib",
            }
        )

    for row in decl_graph.get("nodes", []):
        if not isinstance(row, dict):
            continue
        name = row.get("name")
        module = row.get("module")
        if not isinstance(name, str) or not isinstance(module, str):
            continue
        if name in seen_nodes:
            continue
        seen_nodes.add(name)
        nodes.append(
            {
                "id": name,
                "kind": "decl",
                "title": name.split(".")[-1],
                "layer": module_to_layer.get(module, layer_from_module(module)),
                "spine": (module in canon_modules) or (name in canon_decls) or (name in usage_top),
                "module": module,
                "path": module_to_path.get(module, ""),
                "package": "mathlib" if name.startswith("Mathlib.") else "MLTheory",
            }
        )

    concept_nodes = taxonomy.get("nodes", [])
    for row in concept_nodes:
        if not isinstance(row, dict):
            continue
        cid = row.get("id")
        title = row.get("title")
        if not isinstance(cid, str) or not isinstance(title, str):
            continue
        nid = f"concept:{cid}"
        if nid in seen_nodes:
            continue
        seen_nodes.add(nid)
        nodes.append(
            {
                "id": nid,
                "kind": "concept",
                "title": title,
                "spine": bool(row.get("default_collapsed", False)) is False,
                "package": "MLTheory",
            }
        )

    edges: list[dict] = []
    seen_edges: set[tuple[str, str, str]] = set()

    def add_edge(src: str, dst: str, etype: str, weight: float | None = None):
        if src not in seen_nodes or dst not in seen_nodes:
            return
        key = (src, dst, etype)
        if key in seen_edges:
            return
        seen_edges.add(key)
        row = {"src": src, "dst": dst, "type": etype}
        if weight is not None:
            row["weight"] = float(weight)
        edges.append(row)

    for row in module_graph.get("edges", []):
        if not isinstance(row, dict):
            continue
        src = row.get("src")
        dst = row.get("dst")
        if isinstance(src, str) and isinstance(dst, str):
            add_edge(src, dst, "imports", row.get("weight"))

    for row in mathlib_imports.get("edges", []):
        if not isinstance(row, dict):
            continue
        src = row.get("src")
        dst = row.get("dst")
        if isinstance(src, str) and isinstance(dst, str):
            if src in selected_mathlib and dst in selected_mathlib:
                add_edge(src, dst, "imports", row.get("weight"))

    for row in decl_graph.get("edges", []):
        if not isinstance(row, dict):
            continue
        src = row.get("src")
        dst = row.get("dst")
        etype = row.get("type")
        if isinstance(src, str) and isinstance(dst, str) and isinstance(etype, str):
            add_edge(src, dst, etype)

    for row in decl_graph.get("nodes", []):
        if not isinstance(row, dict):
            continue
        name = row.get("name")
        module = row.get("module")
        if isinstance(name, str) and isinstance(module, str):
            add_edge(name, module, "decl_in_module")

    for row in taxonomy.get("bindings", []):
        if not isinstance(row, dict):
            continue
        node = row.get("node")
        target = row.get("target")
        if not isinstance(node, str) or not isinstance(target, str):
            continue
        add_edge(f"concept:{node}", target, "binds")

    for row in usage_graph.get("edges", []):
        if not isinstance(row, dict):
            continue
        src = row.get("src")
        dst = row.get("dst")
        w = row.get("weight", 1.0)
        if isinstance(src, str) and isinstance(dst, str):
            add_edge(src, dst, "used_recently", float(w))

    mapping = mltheory_to_mathlib.get("mapping") or mltheory_to_mathlib.get("module_mappings") or {}
    if isinstance(mapping, dict):
        for module_id, row in mapping.items():
            if not isinstance(module_id, str) or module_id not in seen_nodes:
                continue
            if not isinstance(row, dict):
                continue
            direct = row.get("direct", [])
            if not isinstance(direct, list):
                continue
            for dep in direct:
                if isinstance(dep, str) and dep in seen_nodes:
                    add_edge(module_id, dep, "imports", 1.0)

    payload = {
        "generated_at": str(date.today()),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": sorted(nodes, key=lambda n: (n["kind"], n["id"])),
        "edges": sorted(edges, key=lambda e: (e["type"], e["src"], e["dst"])),
    }

    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    export_path = args.export_docs_data.resolve()
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"[gen_subgraph] wrote {out} and {export_path} "
        f"({len(nodes)} nodes / {len(edges)} edges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
