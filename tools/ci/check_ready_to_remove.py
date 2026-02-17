#!/usr/bin/env python3
"""Gate for cleanup release-window state transitions."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"
WINDOW_RE = re.compile(r"^([0-9]+)\s+release(?:s)?$")


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    meta = data.get("meta", {})
    current_epoch = meta.get("cleanup_release_epoch")
    candidates = data.get("structure_cleanup_candidates", [])

    errors: list[str] = []
    lines: list[str] = []

    if not isinstance(current_epoch, int) or current_epoch < 1:
        errors.append("meta.cleanup_release_epoch must be integer >= 1")
        current_epoch = 1

    if not isinstance(candidates, list):
        errors.append("structure_cleanup_candidates must be an array")
        candidates = []
    elif not candidates:
        print(
            "[check_ready_to_remove] passed: "
            f"current cleanup_release_epoch={current_epoch}, candidates=0 (nothing to track)"
        )
        return 0

    for i, c in enumerate(candidates):
        label = f"structure_cleanup_candidates[{i}]"
        module_path = c.get("module_path", f"<{label}>")
        state = c.get("execution_state")
        window = c.get("compatibility_window")
        remove_after = c.get("remove_after_releases")
        started = c.get("migration_started_epoch")

        if not isinstance(module_path, str) or not module_path:
            errors.append(f"{label}.module_path invalid")
            continue
        if not isinstance(state, str) or not state:
            errors.append(f"{label}.execution_state invalid")
            continue
        if not isinstance(window, str) or not WINDOW_RE.match(window):
            errors.append(f"{label}.compatibility_window invalid: {window}")
            continue
        if not isinstance(remove_after, int) or remove_after < 1:
            errors.append(f"{label}.remove_after_releases invalid: {remove_after}")
            continue
        if not isinstance(started, int) or started < 1:
            errors.append(f"{label}.migration_started_epoch invalid: {started}")
            continue

        ready_epoch = started + remove_after
        ready_now = current_epoch >= ready_epoch
        due_in = ready_epoch - current_epoch

        lines.append(
            f"{module_path}: state={state}, current={current_epoch}, "
            f"ready_epoch={ready_epoch}, due_in={due_in if due_in > 0 else 0}"
        )

        if state == "ready_to_remove" and not ready_now:
            errors.append(
                f"{module_path}: state=ready_to_remove too early; "
                f"current={current_epoch}, ready_epoch={ready_epoch}"
            )
        elif state != "ready_to_remove" and ready_now:
            errors.append(
                f"{module_path}: window reached (current={current_epoch} >= {ready_epoch}); "
                "set execution_state=ready_to_remove or adjust release metadata"
            )

    if errors:
        print("[check_ready_to_remove] failed:")
        for err in errors:
            print(f"- {err}")
        if lines:
            print("[check_ready_to_remove] details:")
            for line in lines:
                print(f"  * {line}")
        return 1

    print(
        "[check_ready_to_remove] passed: "
        f"current cleanup_release_epoch={current_epoch}, candidates={len(candidates)}"
    )
    for line in lines:
        print(f"  * {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
