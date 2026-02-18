#!/usr/bin/env python3
"""Advance cleanup release epoch and auto-transition due candidates."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"


def ordered_registry(data: dict) -> dict:
    return {
        "meta": data.get("meta", {}),
        "decisions": data.get("decisions", []),
        "taxonomy_nodes": data.get("taxonomy_nodes", []),
        "taxonomy_relations": data.get("taxonomy_relations", []),
        "official_workflow_refs": data.get("official_workflow_refs", []),
        "canonical_specs": data.get("canonical_specs", []),
        "modules": data.get("modules", []),
        "planned_modules": data.get("planned_modules", []),
        "structure_cleanup_candidates": data.get("structure_cleanup_candidates", []),
        "gaps": data.get("gaps", []),
        "books": data.get("books", []),
        "aliases": data.get("aliases", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Advance cleanup release epoch and auto-mark due candidates as ready_to_remove."
    )
    parser.add_argument(
        "--to",
        type=int,
        default=None,
        help="Target cleanup_release_epoch. Default: current + 1.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write changes to registry.json. Without this flag, run in dry-run mode.",
    )
    args = parser.parse_args()

    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    meta = data.setdefault("meta", {})
    current_epoch = int(meta.get("cleanup_release_epoch", 1))
    target_epoch = args.to if args.to is not None else current_epoch + 1
    if target_epoch < current_epoch:
        raise SystemExit(
            f"[advance_cleanup_release_epoch] target epoch {target_epoch} < current epoch {current_epoch}"
        )

    candidates = data.get("structure_cleanup_candidates", [])
    if not isinstance(candidates, list):
        raise SystemExit("[advance_cleanup_release_epoch] structure_cleanup_candidates must be an array")

    transitioned: list[str] = []
    details: list[str] = []
    for c in candidates:
        module_path = str(c.get("module_path", ""))
        state = str(c.get("execution_state", ""))
        remove_after = c.get("remove_after_releases")
        started = c.get("migration_started_epoch")
        if not module_path:
            continue
        if not isinstance(remove_after, int) or remove_after < 1:
            raise SystemExit(
                f"[advance_cleanup_release_epoch] invalid remove_after_releases for {module_path}: {remove_after}"
            )
        if not isinstance(started, int) or started < 1:
            raise SystemExit(
                f"[advance_cleanup_release_epoch] invalid migration_started_epoch for {module_path}: {started}"
            )

        ready_epoch = started + remove_after
        due = target_epoch >= ready_epoch
        details.append(
            f"{module_path}: state={state}, target_epoch={target_epoch}, ready_epoch={ready_epoch}, due={due}"
        )

        if due and state in {"migrating", "deprecated_announced"}:
            c["execution_state"] = "ready_to_remove"
            transitioned.append(module_path)

    meta["cleanup_release_epoch"] = target_epoch
    meta["last_updated"] = str(date.today())
    policy = meta.setdefault("policy", [])
    if "cleanup_release_epoch_advanced_by_script" not in policy:
        policy.append("cleanup_release_epoch_advanced_by_script")

    if transitioned:
        msg = (
            f"advance cleanup_release_epoch arrive {target_epoch},and switch the expiration candidate to ready_to_remove:"
            + " / ".join(transitioned)
            + "."
        )
    else:
        msg = f"advance cleanup_release_epoch arrive {target_epoch},This time there are no candidates to expire and switch to ready_to_remove."

    decision = {
        "date": str(date.today()),
        "decision": msg,
        "status": "active",
        "impact": "release Window advancement is implemented uniformly through scripts,ready_to_remove Transformations are reproducible and auditable.",
    }
    if decision["decision"] not in {d.get("decision") for d in data.get("decisions", [])}:
        data.setdefault("decisions", []).append(decision)

    print(
        "[advance_cleanup_release_epoch] "
        f"{'write' if args.write else 'dry-run'} mode: {current_epoch} -> {target_epoch}"
    )
    for line in details:
        print(f"  * {line}")
    if transitioned:
        print(f"[advance_cleanup_release_epoch] transitioned: {', '.join(transitioned)}")
    else:
        print("[advance_cleanup_release_epoch] transitioned: none")

    if args.write:
        REGISTRY.write_text(
            json.dumps(ordered_registry(data), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[advance_cleanup_release_epoch] wrote {REGISTRY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
