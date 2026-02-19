#!/usr/bin/env python3
"""Capture versioned graph snapshots and emit embedded dataset bundle for GraphExplorer."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


GRAPH_FILES = (
    "module_graph.json",
    "decl_graph.json",
    "usage_graph.json",
    "subgraph.json",
)

INDEX_FILES = (
    "modules.json",
    "imports.json",
    "decls.json",
    "usage_suggestions.json",
    "mathlib_modules.json",
    "mathlib_imports.json",
    "mathlib_hubs.json",
    "mathlib_aggregators.json",
    "mathlib_slice.json",
    "mltheory_to_mathlib.json",
)

META_FILES = (
    "domains.yaml",
    "domain_profiles.yaml",
    "taxonomy.yaml",
    "taxonomy_math.yaml",
    "taxonomy_applied.yaml",
    "tags_overrides.yaml",
)

TELEMETRY_FILES = (
    "retrieval.jsonl",
    "usage_events.jsonl",
)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    default_snapshot = datetime.now(timezone.utc).date().isoformat()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=str(root), help="MLTheory repository root")
    ap.add_argument("--snapshot-id", default=default_snapshot, help="snapshot identifier")
    ap.add_argument(
        "--snapshots-root",
        default="artifacts/_snapshots",
        help="snapshot storage directory (relative to repo root unless absolute)",
    )
    ap.add_argument(
        "--docs-auto",
        default="docs/_auto",
        help="docs _auto directory (relative to repo root unless absolute)",
    )
    ap.add_argument(
        "--out-bundle-js",
        default="docs/_auto/snapshot_datasets_bundle.js",
        help="output JS bundle path",
    )
    ap.add_argument(
        "--max-bundle-snapshots",
        type=int,
        default=12,
        help="max historical snapshots embedded in JS bundle",
    )
    ap.add_argument(
        "--skip-capture",
        action="store_true",
        help="do not capture current snapshot, only rebuild bundle from existing snapshots",
    )
    return ap.parse_args()


def resolve_path(root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return (root / path).resolve()


def safe_copy(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("nodes"), list) or not isinstance(data.get("edges"), list):
        return None
    return data


def capture_snapshot(repo_root: Path, snapshots_root: Path, snapshot_id: str) -> tuple[Path, int]:
    snapshot_dir = snapshots_root / snapshot_id
    if snapshot_dir.exists():
        shutil.rmtree(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for name in GRAPH_FILES:
        if safe_copy(
            repo_root / "artifacts" / "graphs" / name,
            snapshot_dir / "graphs" / name,
        ):
            copied += 1
    for name in INDEX_FILES:
        if safe_copy(
            repo_root / "artifacts" / "index" / name,
            snapshot_dir / "index" / name,
        ):
            copied += 1
    for name in META_FILES:
        if safe_copy(
            repo_root / "docs" / "meta" / name,
            snapshot_dir / "meta" / name,
        ):
            copied += 1
    for name in TELEMETRY_FILES:
        if safe_copy(
            repo_root / "artifacts" / "telemetry" / name,
            snapshot_dir / "telemetry" / name,
        ):
            copied += 1

    metadata = {
        "snapshot_id": snapshot_id,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "copied_files": copied,
        "graphs": list(GRAPH_FILES),
        "index": list(INDEX_FILES),
        "meta": list(META_FILES),
        "telemetry": list(TELEMETRY_FILES),
    }
    (snapshot_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return snapshot_dir, copied


def collect_snapshot_entries(snapshots_root: Path, max_count: int) -> list[dict]:
    if max_count <= 0 or not snapshots_root.exists():
        return []

    entries: list[dict] = []
    dirs = sorted(
        [p for p in snapshots_root.iterdir() if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )
    for directory in dirs:
        graph = load_json(directory / "graphs" / "subgraph.json")
        if graph is None:
            continue
        snapshot_id = directory.name
        entries.append(
            {
                "id": snapshot_id,
                "label": snapshot_id,
                "node_count": len(graph.get("nodes", [])),
                "edge_count": len(graph.get("edges", [])),
                "subgraph": graph,
            }
        )
        if len(entries) >= max_count:
            break
    return entries


def write_bundle_js(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    text = (
        "/* generated by tools/index/gen_snapshot_bundle.py; do not edit manually */\n"
        "(function () {\n"
        f"  window.__MLTHEORY_DATASETS__ = {encoded};\n"
        "})();\n"
    )
    path.write_text(text, encoding="utf-8")


def write_manifest(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    docs_auto = resolve_path(repo_root, args.docs_auto)
    snapshots_root = resolve_path(repo_root, args.snapshots_root)
    out_bundle_js = resolve_path(repo_root, args.out_bundle_js)

    latest_graph = load_json(docs_auto / "subgraph.json")
    if latest_graph is None:
        raise RuntimeError(
            f"latest subgraph missing or invalid: {docs_auto / 'subgraph.json'}"
        )

    copied_files = 0
    if not args.skip_capture:
        _, copied_files = capture_snapshot(repo_root, snapshots_root, args.snapshot_id)

    history = collect_snapshot_entries(snapshots_root, max(0, args.max_bundle_snapshots))
    datasets = [
        {
            "id": "latest",
            "label": "latest",
            "node_count": len(latest_graph.get("nodes", [])),
            "edge_count": len(latest_graph.get("edges", [])),
            "subgraph": latest_graph,
        }
    ]
    for row in history:
        if row.get("id") == "latest":
            continue
        datasets.append(row)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "default_dataset": "latest",
        "datasets": datasets,
    }
    write_bundle_js(out_bundle_js, payload)

    manifest = {
        "generated_at": payload["generated_at"],
        "default_dataset": "latest",
        "datasets": [
            {
                "id": row["id"],
                "label": row["label"],
                "node_count": row["node_count"],
                "edge_count": row["edge_count"],
            }
            for row in datasets
        ],
    }
    write_manifest(snapshots_root / "manifest.json", manifest)

    print(
        "[gen_snapshot_bundle] wrote "
        f"{out_bundle_js.relative_to(repo_root)} "
        f"(datasets={len(datasets)}, copied_files={copied_files})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
