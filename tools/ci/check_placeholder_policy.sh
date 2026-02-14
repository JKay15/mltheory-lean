#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[check_placeholder_policy] checking Lean sources under Core/Methods..."
if rg -n ':\s*Prop\s*:=\s*True\b' MLTheory/Core MLTheory/Methods; then
  echo "[check_placeholder_policy] failed: Core/Methods contains Prop := True placeholders."
  exit 1
fi

echo "[check_placeholder_policy] checking SSOT policy alignment..."
python3 - <<'PY'
import json
from pathlib import Path

root = Path.cwd()
registry = json.loads((root / "docs/ssot/registry.json").read_text(encoding="utf-8"))

errors = []
for idx, module in enumerate(registry.get("modules", [])):
    layer = module.get("layer")
    proof_status = module.get("proof_status")
    scope = module.get("placeholder_policy_scope")
    path = module.get("module_path", f"<modules[{idx}]>")

    if layer in {"core", "methods"}:
        if scope != "forbidden":
            errors.append(f"{path}: layer={layer} must use placeholder_policy_scope=forbidden")
        if proof_status == "placeholder":
            errors.append(f"{path}: layer={layer} must not keep proof_status=placeholder")

if errors:
    print("[check_placeholder_policy] failed:")
    for err in errors:
        print(f"- {err}")
    raise SystemExit(1)

print("[check_placeholder_policy] passed.")
PY
