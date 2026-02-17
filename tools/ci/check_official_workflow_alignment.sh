#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

python3 - <<'PY'
import json
from pathlib import Path

root = Path.cwd()
registry = json.loads((root / "docs/ssot/registry.json").read_text(encoding="utf-8"))

required_caps = {"Loogle", "LeanSearch", "InfoView/LoogleView", "REPL"}
refs = registry.get("official_workflow_refs", [])
errors = []

if not isinstance(refs, list) or not refs:
    errors.append("official_workflow_refs is missing or empty")
else:
    by_cap = {}
    for i, ref in enumerate(refs):
        cap = ref.get("capability")
        by_cap.setdefault(cap, []).append((i, ref))
        for field in ("source_url", "capability", "local_enforcement", "status"):
            if not str(ref.get(field, "")).strip():
                errors.append(f"official_workflow_refs[{i}].{field} is empty")
        src = str(ref.get("source_url", ""))
        if "lean-lang.org/learn" not in src and "vscode-lean4/manual" not in src:
            errors.append(f"official_workflow_refs[{i}] source_url is not from official baseline")

    for cap in sorted(required_caps):
        active = [
            ref for _, ref in by_cap.get(cap, [])
            if str(ref.get("status", "")).lower() == "active"
        ]
        if not active:
            errors.append(f"missing active official workflow mapping for capability: {cap}")

    # Lightweight semantic checks for local enforcement strings.
    loogle_refs = [ref for _, ref in by_cap.get("Loogle", [])]
    if loogle_refs and not any(
        ("lean_loogle" in ref.get("local_enforcement", ""))
        or ("--loogle-local" in ref.get("local_enforcement", ""))
        for ref in loogle_refs
    ):
        errors.append("Loogle mapping must mention lean_loogle or --loogle-local")

    leansearch_refs = [ref for _, ref in by_cap.get("LeanSearch", [])]
    if leansearch_refs and not any(
        "lean_leansearch" in ref.get("local_enforcement", "") for ref in leansearch_refs
    ):
        errors.append("LeanSearch mapping must mention lean_leansearch")

    infoview_refs = [ref for _, ref in by_cap.get("InfoView/LoogleView", [])]
    if infoview_refs and not any(
        (
            "lean_goal" in ref.get("local_enforcement", "")
            and "lean_diagnostic_messages" in ref.get("local_enforcement", "")
        )
        or (
            "InfoView" in ref.get("local_enforcement", "")
            and "LoogleView" in ref.get("local_enforcement", "")
        )
        for ref in infoview_refs
    ):
        errors.append(
            "InfoView/LoogleView mapping must mention `lean_goal` + `lean_diagnostic_messages` or explicit InfoView/LoogleView review rule"
        )

    repl_refs = [ref for _, ref in by_cap.get("REPL", [])]
    if repl_refs and not any(
        "--repl" in ref.get("local_enforcement", "") for ref in repl_refs
    ):
        errors.append("REPL mapping must mention --repl")

if errors:
    print("[check_official_workflow_alignment] failed:")
    for err in errors:
        print(f"- {err}")
    raise SystemExit(1)

print("[check_official_workflow_alignment] passed.")
PY
