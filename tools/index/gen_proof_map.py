#!/usr/bin/env python3
"""Generate per-problem ProofMap artifacts and UI index."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path


REQUIRED_FILES = (
    "Spec.lean",
    "Cache.lean",
    "Proof.lean",
    "Tasks.yaml",
    "Sources.md",
    "Glossary.yaml",
)
LEAN_FILES = ("Spec.lean", "Sketch.lean", "Cache.lean", "Proof.lean")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_imports(text: str) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("import "):
            continue
        tail = line[len("import ") :].strip()
        if not tail:
            continue
        for token in tail.split():
            if token.startswith("--"):
                break
            clean = token.strip()
            if clean:
                out.append(clean)
    return out


def extract_symbol_refs(text: str) -> list[str]:
    pat = re.compile(r"\b(?:MLTheory|Mathlib|Problems)\.[A-Za-z0-9_']+(?:\.[A-Za-z0-9_']+)+\b")
    return pat.findall(text)


def extract_local_decls(text: str) -> list[str]:
    pat = re.compile(
        r"^\s*(?:theorem|lemma|def|abbrev|structure|class|inductive)\s+([A-Za-z0-9_']+)",
        flags=re.MULTILINE,
    )
    return pat.findall(text)


def safe_id(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", raw).strip("_")


def find_problem_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for spec in root.rglob("Spec.lean"):
        parent = spec.parent
        rel = parent.relative_to(root)
        if len(rel.parts) < 2:
            continue
        out.append(parent)
    out.sort()
    return out


def build_problem_map(
    *,
    root: Path,
    problem_dir: Path,
    subgraph_nodes_by_id: dict[str, dict],
    subgraph_edges: list[dict],
    top_refs: int,
) -> dict:
    rel = problem_dir.relative_to(root)
    suite = rel.parts[1]
    problem = rel.parts[2]
    problem_id = f"{suite}/{problem}"

    source_files: list[str] = []
    imports: list[str] = []
    local_decl_rows: list[dict] = []
    ref_counter: Counter[str] = Counter()

    for fname in LEAN_FILES:
        p = problem_dir / fname
        if not p.exists():
            continue
        source_files.append(fname)
        text = p.read_text(encoding="utf-8")
        imports.extend(extract_imports(text))
        refs = extract_symbol_refs(text)
        for ref in refs:
            if ref in subgraph_nodes_by_id:
                ref_counter[ref] += 1
        local_decls = sorted(set(extract_local_decls(text)))
        local_decl_rows.append({"file": fname, "decls": local_decls})

    imports = sorted(set(imports))
    referenced_decls: list[dict] = []
    for node_id, count in ref_counter.most_common(top_refs):
        node = subgraph_nodes_by_id.get(node_id, {})
        referenced_decls.append(
            {
                "id": node_id,
                "count": int(count),
                "kind": node.get("kind", ""),
                "module": node.get("module", "")
                if isinstance(node.get("module", ""), str)
                else "",
            }
        )

    selected_ids: set[str] = {row["id"] for row in referenced_decls}
    for node_id in list(selected_ids):
        node = subgraph_nodes_by_id.get(node_id, {})
        module = node.get("module", "")
        if isinstance(module, str) and module in subgraph_nodes_by_id:
            selected_ids.add(module)

    for module in imports:
        if module in subgraph_nodes_by_id:
            selected_ids.add(module)

    edge_neighbor_types = {"decl_in_module", "uses_type", "uses_value", "imports", "contains"}
    for edge in subgraph_edges:
        if not isinstance(edge, dict):
            continue
        edge_type = edge.get("type")
        src = edge.get("src")
        dst = edge.get("dst")
        if edge_type not in edge_neighbor_types:
            continue
        if not isinstance(src, str) or not isinstance(dst, str):
            continue
        if src in selected_ids or dst in selected_ids:
            if src in subgraph_nodes_by_id:
                selected_ids.add(src)
            if dst in subgraph_nodes_by_id:
                selected_ids.add(dst)

    node_key_keep = (
        "id",
        "kind",
        "title",
        "layer",
        "module",
        "path",
        "package",
        "profiles",
        "math_tags",
        "applied_tags",
        "usage_count",
        "usage_success_count",
        "usage_last_used",
        "retrieval_hit_count",
        "retrieval_final_hit_count",
        "retrieval_last_query",
        "retrieval_last_stage",
        "retrieval_last_source",
        "retrieval_last_seen",
    )
    nodes = []
    for node_id in sorted(selected_ids):
        node = subgraph_nodes_by_id.get(node_id)
        if not isinstance(node, dict):
            continue
        nodes.append({k: node.get(k) for k in node_key_keep if k in node})

    edge_key_keep = ("src", "dst", "type", "weight", "domains", "math_tags", "applied_tags")
    edges = []
    for edge in subgraph_edges:
        if not isinstance(edge, dict):
            continue
        src = edge.get("src")
        dst = edge.get("dst")
        if not isinstance(src, str) or not isinstance(dst, str):
            continue
        if src not in selected_ids or dst not in selected_ids:
            continue
        edges.append({k: edge.get(k) for k in edge_key_keep if k in edge})
    edges.sort(key=lambda e: (e.get("type", ""), e.get("src", ""), e.get("dst", "")))

    return {
        "generated_at": str(date.today()),
        "problem_id": problem_id,
        "suite": suite,
        "problem": problem,
        "problem_path": str(problem_dir.relative_to(root)),
        "source_files": source_files,
        "imports": imports,
        "local_decls": local_decl_rows,
        "referenced_decls": referenced_decls,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--subgraph",
        type=Path,
        default=Path("artifacts/graphs/subgraph.json"),
        help="subgraph.json path",
    )
    ap.add_argument(
        "--problems-root",
        type=Path,
        default=Path("Problems"),
        help="Problems root directory",
    )
    ap.add_argument(
        "--docs-auto",
        type=Path,
        default=Path("docs/_auto"),
        help="docs/_auto root",
    )
    ap.add_argument(
        "--out-index",
        type=Path,
        default=Path("docs/_auto/proof_maps.json"),
        help="proof map index JSON path",
    )
    ap.add_argument(
        "--out-bundle-js",
        type=Path,
        default=Path("docs/_auto/proof_maps_bundle.js"),
        help="embedded proof map bundle js path (for file:// mode)",
    )
    ap.add_argument("--top-refs", type=int, default=60, help="top referenced declaration cap")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    subgraph_path = args.subgraph if args.subgraph.is_absolute() else root / args.subgraph
    problems_root = args.problems_root if args.problems_root.is_absolute() else root / args.problems_root
    docs_auto_root = args.docs_auto if args.docs_auto.is_absolute() else root / args.docs_auto
    index_path = args.out_index if args.out_index.is_absolute() else root / args.out_index
    bundle_js_path = args.out_bundle_js if args.out_bundle_js.is_absolute() else root / args.out_bundle_js

    subgraph = load_json(subgraph_path.resolve()) if subgraph_path.exists() else {"nodes": [], "edges": []}
    subgraph_nodes = subgraph.get("nodes", [])
    subgraph_edges = subgraph.get("edges", [])
    if not isinstance(subgraph_nodes, list):
        subgraph_nodes = []
    if not isinstance(subgraph_edges, list):
        subgraph_edges = []
    nodes_by_id = {
        node["id"]: node
        for node in subgraph_nodes
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }

    mirror_dir = docs_auto_root / "proof_maps"
    mirror_dir.mkdir(parents=True, exist_ok=True)
    for stale in mirror_dir.glob("*.json"):
        stale.unlink()

    entries: list[dict] = []
    embedded_maps: dict[str, dict] = {}
    problem_dirs = find_problem_dirs(problems_root)
    for problem_dir in problem_dirs:
        rel = problem_dir.relative_to(root)
        suite = rel.parts[1]
        problem = rel.parts[2]
        missing_required = [name for name in REQUIRED_FILES if not (problem_dir / name).exists()]
        if missing_required:
            continue

        payload = build_problem_map(
            root=root,
            problem_dir=problem_dir,
            subgraph_nodes_by_id=nodes_by_id,
            subgraph_edges=subgraph_edges,
            top_refs=max(1, int(args.top_refs)),
        )

        problem_map_path = problem_dir / "ProofMap.json"
        problem_map_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        mirror_name = f"{safe_id(payload['problem_id'])}.json"
        mirror_path = mirror_dir / mirror_name
        mirror_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        embedded_maps[f"./_auto/proof_maps/{mirror_name}"] = payload

        entries.append(
            {
                "id": payload["problem_id"],
                "suite": suite,
                "problem": problem,
                "problem_path": str(problem_dir.relative_to(root)),
                "proof_map": f"./_auto/proof_maps/{mirror_name}",
                "node_count": payload["node_count"],
                "edge_count": payload["edge_count"],
                "referenced_decl_count": len(payload["referenced_decls"]),
                "import_count": len(payload["imports"]),
            }
        )

    entries.sort(key=lambda row: (row["suite"], row["problem"]))
    index_payload = {
        "generated_at": str(date.today()),
        "problem_count": len(entries),
        "problems": entries,
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    bundle_js_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_js_path.write_text(
        "window.__MLTHEORY_PROOF_MAP_INDEX__ = "
        + json.dumps(index_payload, ensure_ascii=False)
        + ";\n"
        + "window.__MLTHEORY_PROOF_MAPS__ = "
        + json.dumps(embedded_maps, ensure_ascii=False)
        + ";\n",
        encoding="utf-8",
    )
    print(f"[gen_proof_map] wrote {index_path} (problems={len(entries)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
