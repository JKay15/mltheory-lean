#!/usr/bin/env python3
"""Generate Lean import graph artifacts from source files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path


def module_name(src_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(src_root.parent).with_suffix("")
    return ".".join(rel.parts)


def parse_imports(line: str) -> list[str]:
    if "--" in line:
        line = line.split("--", 1)[0]
    line = line.strip()
    if not line.startswith("import "):
        return []
    tail = line[len("import ") :].strip()
    if not tail:
        return []
    return tail.split()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True, help="Lean source root")
    ap.add_argument("--out", type=Path, required=True, help="Output JSON path")
    ap.add_argument(
        "--package",
        type=str,
        default="MLTheory",
        help="Package label: MLTheory|mathlib|std|other",
    )
    args = ap.parse_args()

    src = args.src.resolve()
    out = args.out.resolve()

    nodes: set[str] = set()
    edge_set: set[tuple[str, str]] = set()

    for lean_file in sorted(src.rglob("*.lean")):
        src_mod = module_name(src, lean_file)
        nodes.add(src_mod)
        for raw in lean_file.read_text(encoding="utf-8").splitlines():
            for dst_mod in parse_imports(raw):
                nodes.add(dst_mod)
                edge_set.add((src_mod, dst_mod))

    edges = [
        {"src": src_mod, "dst": dst_mod, "type": "imports", "package": args.package}
        for (src_mod, dst_mod) in sorted(edge_set)
    ]
    fan_out = Counter(src_mod for (src_mod, _) in edge_set)
    fan_in = Counter(dst_mod for (_, dst_mod) in edge_set)
    payload = {
        "generated_at": str(date.today()),
        "package": args.package,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": sorted(nodes),
        "edges": edges,
        "fan_in": {k: fan_in[k] for k in sorted(fan_in)},
        "fan_out": {k: fan_out[k] for k in sorted(fan_out)},
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[gen_imports] wrote {out} ({len(nodes)} nodes / {len(edges)} edges)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
