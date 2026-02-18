#!/usr/bin/env python3
"""Build module-level graph artifact from modules/imports indexes."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modules", type=Path, required=True, help="modules.json path")
    ap.add_argument("--imports", type=Path, required=True, help="imports.json path")
    ap.add_argument("--out", type=Path, required=True, help="module_graph.json output path")
    args = ap.parse_args()

    modules = load_json(args.modules.resolve())
    imports = load_json(args.imports.resolve())
    out = args.out.resolve()

    module_rows = modules.get("modules", [])
    module_ids = {m["module"] for m in module_rows if isinstance(m, dict) and "module" in m}
    layer_map = {m["module"]: m.get("layer", "other") for m in module_rows if "module" in m}

    graph_nodes = [
        {
            "id": module_name,
            "kind": "module",
            "title": module_name,
            "layer": layer_map.get(module_name, "other"),
        }
        for module_name in sorted(module_ids)
    ]

    graph_edges = []
    for edge in imports.get("edges", []):
        if not isinstance(edge, dict):
            continue
        src = edge.get("src")
        dst = edge.get("dst")
        if not isinstance(src, str) or not isinstance(dst, str):
            continue
        if src not in module_ids or dst not in module_ids:
            continue
        graph_edges.append({"src": src, "dst": dst, "type": "imports", "weight": 1.0})

    payload = {
        "generated_at": str(date.today()),
        "nodes": graph_nodes,
        "edges": sorted(graph_edges, key=lambda e: (e["src"], e["dst"])),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"[gen_module_graph] wrote {out} "
        f"({len(graph_nodes)} nodes / {len(graph_edges)} edges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
