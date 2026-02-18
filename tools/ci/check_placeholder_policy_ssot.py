#!/usr/bin/env python3
"""Check placeholder policy fields in docs/ssot/registry.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    errors: list[str] = []

    for idx, module in enumerate(registry.get("modules", [])):
        if not isinstance(module, dict):
            continue
        layer = module.get("layer")
        proof_status = module.get("proof_status")
        scope = module.get("placeholder_policy_scope")
        path = module.get("module_path", f"<modules[{idx}]>")

        if layer in {"core", "methods"}:
            if scope != "forbidden":
                errors.append(
                    f"{path}: layer={layer} must use placeholder_policy_scope=forbidden"
                )
            if proof_status == "placeholder":
                errors.append(f"{path}: layer={layer} must not keep proof_status=placeholder")

    if errors:
        print("[check_placeholder_policy_ssot] failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("[check_placeholder_policy_ssot] passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
