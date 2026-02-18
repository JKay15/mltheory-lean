#!/usr/bin/env python3
"""Generate usage graph and spine/import suggestions from telemetry events."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import date
from itertools import combinations
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    events: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                events.append(row)
    return events


def module_of_decl(name: str, decl_to_module: dict[str, str]) -> str:
    module = decl_to_module.get(name)
    if module is not None:
        return module
    parts = name.split(".")
    if len(parts) <= 1:
        return ""
    return ".".join(parts[:-1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--events",
        type=Path,
        default=Path("artifacts/telemetry/usage_events.jsonl"),
        help="usage events jsonl path",
    )
    ap.add_argument("--decl-graph", type=Path, required=True, help="decl_graph.json path")
    ap.add_argument("--out", type=Path, required=True, help="usage_graph.json output path")
    ap.add_argument(
        "--suggestions-out",
        type=Path,
        required=True,
        help="usage_suggestions.json output path",
    )
    ap.add_argument("--top-k", type=int, default=30, help="top-k suggestions")
    args = ap.parse_args()

    decl_graph = load_json(args.decl_graph.resolve())
    decl_nodes = decl_graph.get("nodes", [])

    decl_to_module: dict[str, str] = {}
    for node in decl_nodes:
        if not isinstance(node, dict):
            continue
        name = node.get("name")
        module = node.get("module")
        if isinstance(name, str) and isinstance(module, str):
            decl_to_module[name] = module

    events = load_events(args.events.resolve())
    usage_count: Counter[str] = Counter()
    success_count: Counter[str] = Counter()
    last_used: dict[str, str] = {}
    pair_count: Counter[tuple[str, str]] = Counter()

    for ev in events:
        used_raw = ev.get("used_decls", [])
        if not isinstance(used_raw, list):
            continue
        used = sorted({x for x in used_raw if isinstance(x, str) and x})
        if not used:
            continue
        is_success = str(ev.get("status", "success")) == "success"
        ts = str(ev.get("timestamp", ""))

        for d in used:
            usage_count[d] += 1
            if is_success:
                success_count[d] += 1
            if ts and (d not in last_used or ts > last_used[d]):
                last_used[d] = ts

        for a, b in combinations(used, 2):
            pair_count[(a, b)] += 1

    nodes = []
    for d, cnt in usage_count.items():
        succ = success_count.get(d, 0)
        score = 2 * succ + cnt
        nodes.append(
            {
                "id": d,
                "kind": "decl",
                "title": d.split(".")[-1],
                "module": module_of_decl(d, decl_to_module),
                "usage_count": cnt,
                "success_count": succ,
                "score": score,
                "last_used": last_used.get(d, ""),
            }
        )
    nodes.sort(key=lambda n: (-n["score"], -n["usage_count"], n["id"]))

    edges = [
        {"src": a, "dst": b, "type": "used_recently", "weight": w}
        for (a, b), w in sorted(pair_count.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    usage_graph = {
        "generated_at": str(date.today()),
        "event_count": len(events),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }

    top_k = max(1, args.top_k)
    spine_candidates = [n["id"] for n in nodes[:top_k]]
    module_counter: Counter[str] = Counter()
    for n in nodes[: top_k * 2]:
        module = n.get("module", "")
        if isinstance(module, str) and module:
            module_counter[module] += int(n.get("score", 0))
    module_candidates = [m for m, _ in module_counter.most_common(top_k)]

    suggestions = {
        "generated_at": str(date.today()),
        "event_count": len(events),
        "spine_candidates": spine_candidates,
        "entry_module_candidates": module_candidates,
        "notes": [
            "spine_candidates ranked by usage score (2*success + usage_count)",
            "entry_module_candidates aggregated from top usage decl modules",
        ],
    }

    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(usage_graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    suggestions_out = args.suggestions_out.resolve()
    suggestions_out.parent.mkdir(parents=True, exist_ok=True)
    suggestions_out.write_text(
        json.dumps(suggestions, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"[gen_usage_graph] wrote {out} and {suggestions_out} "
        f"(events={len(events)}, nodes={len(nodes)}, edges={len(edges)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
