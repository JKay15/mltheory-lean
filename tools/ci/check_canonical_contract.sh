#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

python3 - <<'PY'
import json
import re
import subprocess
from pathlib import Path

root = Path.cwd()
registry = json.loads((root / "docs/ssot/registry.json").read_text(encoding="utf-8"))
specs = registry.get("canonical_specs", [])
modules = registry.get("modules", [])

errors = []
warnings = []

if not isinstance(specs, list) or not specs:
    errors.append("canonical_specs is missing or empty")
if not isinstance(modules, list) or not modules:
    errors.append("modules is missing or empty")

decl_to_module_refs = {}
for mod in modules if isinstance(modules, list) else []:
    mpath = str(mod.get("module_path", ""))
    role = str(mod.get("role", ""))
    surface = str(mod.get("user_surface", ""))
    refs = mod.get("formal_decl_refs", [])
    if not isinstance(refs, list):
        continue
    for ref in refs:
        if not ref:
            continue
        decl_to_module_refs.setdefault(ref, []).append(
            {
                "module_path": mpath,
                "role": role,
                "user_surface": surface,
            }
        )


def resolve_path(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else (root / p)


def extract_decl_block(text: str, decl: str) -> str | None:
    pat = re.compile(rf"^\s*(theorem|def|abbrev|lemma|structure)\s+{re.escape(decl)}\b")
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if pat.search(line):
            start = i
            break
    if start is None:
        return None
    out = []
    for line in lines[start:]:
        out.append(line)
        if ":= by" in line or "where" in line:
            break
    return "\n".join(out)


for i, spec in enumerate(specs):
    sid = spec.get("spec_id", f"<spec:{i}>")
    status = str(spec.get("status", "active")).lower()
    if status != "active":
        continue

    repo = spec.get("repo")
    if repo != "MLTheory":
        warnings.append(f"{sid}: external repo `{repo}` skipped in MLTheory gate")
        continue

    entry_file = resolve_path(str(spec.get("entry_file", "")))
    entry_decl = str(spec.get("entry_decl", "")).strip()
    required_refs = spec.get("required_decl_refs", [])
    forbidden_tokens = spec.get("forbidden_tokens", [])

    if not entry_file.exists():
        errors.append(f"{sid}: entry_file missing: {entry_file}")
        continue
    if not entry_decl:
        errors.append(f"{sid}: empty entry_decl")
        continue

    text = entry_file.read_text(encoding="utf-8")
    block = extract_decl_block(text, entry_decl)
    if block is None:
        errors.append(f"{sid}: declaration `{entry_decl}` not found in {entry_file}")
        continue

    for tok in forbidden_tokens:
        if tok and re.search(tok, block):
            errors.append(f"{sid}: forbidden token `{tok}` found in declaration block")

    # Canonical entry lock must be anchored in SSOT module mapping.
    entry_maps = [
        m for m in decl_to_module_refs.get(entry_decl, [])
        if m["role"] == "canonical" and m["user_surface"] == "public"
    ]
    if not entry_maps:
        errors.append(
            f"{sid}: entry_decl `{entry_decl}` is not mapped by any canonical/public module formal_decl_refs"
        )

    for ref in required_refs:
        rg = subprocess.run(
            ["rg", "-n", rf"\b{re.escape(ref)}\b", "MLTheory", "MLTheory.lean"],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if rg.returncode != 0:
            errors.append(f"{sid}: required_decl_ref `{ref}` not found in MLTheory")
            continue

        # Intermediate/canonical mapping traceability:
        # each required declaration must be surfaced by canonical/compat/bridge modules.
        allowed_roles = {"canonical", "compat", "bridge"}
        mapped = [
            m for m in decl_to_module_refs.get(ref, [])
            if m["role"] in allowed_roles
        ]
        if not mapped:
            errors.append(
                f"{sid}: required_decl_ref `{ref}` missing traceable module mapping in formal_decl_refs (roles: canonical/compat/bridge)"
            )

    # Axiom policy (lightweight declaration-level guard)
    if str(spec.get("axiom_policy", "")).lower() == "standard_only":
        if re.search(r"\baxiom\b", text):
            errors.append(f"{sid}: source file contains `axiom` under standard_only policy")

if errors:
    print("[check_canonical_contract] failed:")
    for err in errors:
        print(f"- {err}")
    for warn in warnings:
        print(f"[warn] {warn}")
    raise SystemExit(1)

for warn in warnings:
    print(f"[check_canonical_contract] warn: {warn}")
print("[check_canonical_contract] passed.")
PY
