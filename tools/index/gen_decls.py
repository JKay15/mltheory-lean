#!/usr/bin/env python3
"""Generate decls index from decl_graph + module index."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decl-graph", type=Path, required=True, help="decl_graph.json path")
    ap.add_argument("--modules", type=Path, required=True, help="modules.json path")
    ap.add_argument("--out", type=Path, required=True, help="decls.json output path")
    args = ap.parse_args()

    decl_graph = load_json(args.decl_graph.resolve())
    modules = load_json(args.modules.resolve())
    out = args.out.resolve()

    module_to_path = {}
    for row in modules.get("modules", []):
        if not isinstance(row, dict):
            continue
        module = row.get("module")
        path = row.get("path")
        if isinstance(module, str) and isinstance(path, str):
            module_to_path[module] = path

    seen: set[str] = set()
    decls: list[dict] = []
    for node in decl_graph.get("nodes", []):
        if not isinstance(node, dict):
            continue
        name = node.get("name")
        module = node.get("module")
        node_kind = node.get("kind")
        decl_kind = node.get("decl_kind")
        kind = decl_kind if isinstance(decl_kind, str) and decl_kind else node_kind
        if not isinstance(name, str) or not isinstance(module, str) or not isinstance(kind, str):
            continue
        if name in seen:
            continue
        seen.add(name)
        rec = {
            "name": name,
            "kind": kind,
            "module": module,
            "package": "MLTheory",
        }
        if isinstance(node_kind, str):
            rec["node_kind"] = node_kind
        generated = node.get("generated")
        if isinstance(generated, bool):
            rec["generated"] = generated
        path = module_to_path.get(module)
        if path is not None:
            rec["path"] = path
        decls.append(rec)

    decls.sort(key=lambda r: r["name"])
    payload = {
        "generated_at": str(date.today()),
        "package": "MLTheory",
        "decl_count": len(decls),
        "decls": decls,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[gen_decls] wrote {out} ({len(decls)} decls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
