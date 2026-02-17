#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ALLOWLIST_FILE="${1:-$ROOT_DIR/tools/ci/deprecated_import_allowlist.txt}"

cd "$ROOT_DIR"

python3 - "$ROOT_DIR" "$ALLOWLIST_FILE" <<'PY'
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
ALLOWLIST_PATH = Path(sys.argv[2]).resolve()
REGISTRY_PATH = ROOT / "docs/ssot/registry.json"

ACTIVE_STATES = {"deprecated_announced", "migrating", "ready_to_remove"}
EXCLUDE_DIRS = {
    ".git",
    ".lake",
    ".elan",
    "build",
    ".cache",
    ".direnv",
    ".venv",
    ".uv-cache",
    ".mypy_cache",
    ".pytest_cache",
    ".agents",
}


def iter_lean_files(repo_root: Path):
    for path in repo_root.rglob("*.lean"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        yield path


def parse_imports(line: str):
    # Accept `import A B C` and strip inline comments.
    m = re.match(r"^\s*import\s+(.+?)\s*$", line)
    if not m:
        return []
    payload = m.group(1).split("--", 1)[0].strip()
    if not payload:
        return []
    modules = []
    for tok in payload.split():
        if re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", tok):
            modules.append(tok)
    return modules


if not REGISTRY_PATH.exists():
    raise SystemExit(f"[check_no_new_deprecated_imports] missing registry: {REGISTRY_PATH}")

data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
candidates = data.get("structure_cleanup_candidates", [])
aliases = data.get("aliases", [])

candidate_modules = sorted(
    {
        c.get("module_path")
        for c in candidates
        if isinstance(c, dict)
        and isinstance(c.get("module_path"), str)
        and c.get("execution_state") in ACTIVE_STATES
    }
)

deprecated_alias_modules = sorted(
    {
        a.get("legacy_module")
        for a in aliases
        if isinstance(a, dict)
        and isinstance(a.get("legacy_module"), str)
        and a.get("status") == "deprecated"
    }
)

retired_modules = sorted(set(deprecated_alias_modules) - set(candidate_modules))
tracked_modules = sorted(set(candidate_modules) | set(retired_modules))

if not tracked_modules:
    print("[check_no_new_deprecated_imports] no tracked deprecated modules; skip.")
    raise SystemExit(0)

repo_roots = [("mltheory", ROOT)]
optional_roots = [
    ("paper-template", ROOT.parent / "paper-template"),
    ("lean-proof-skills", ROOT.parent / "lean-proof-skills"),
]
for alias, path in optional_roots:
    if path.exists():
        repo_roots.append((alias, path.resolve()))
    else:
        print(f"[check_no_new_deprecated_imports] info: skip missing repo root {path}")

findings = set()
for alias, repo_root in repo_roots:
    for file_path in iter_lean_files(repo_root):
        rel_path = file_path.relative_to(repo_root).as_posix()
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line in text.splitlines():
            for imported in parse_imports(line):
                if imported in tracked_modules:
                    findings.add((alias, rel_path, imported))

allowset = set()
parse_errors = []
if candidate_modules:
    if not ALLOWLIST_PATH.exists():
        raise SystemExit(
            f"[check_no_new_deprecated_imports] allowlist missing: {ALLOWLIST_PATH}\n"
            "Create it or pass an explicit allowlist path."
        )
    for lineno, raw in enumerate(ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3 or not all(parts):
            parse_errors.append(f"allowlist:{lineno}: expected `repo_alias|path/to/File.lean|Module.Path`")
            continue
        allowset.add((parts[0], parts[1], parts[2]))
elif ALLOWLIST_PATH.exists():
    # Keep parsing in no-candidate mode so malformed allowlist still gets surfaced.
    for lineno, raw in enumerate(ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3 or not all(parts):
            parse_errors.append(f"allowlist:{lineno}: expected `repo_alias|path/to/File.lean|Module.Path`")
            continue
        allowset.add((parts[0], parts[1], parts[2]))

if parse_errors:
    print("[check_no_new_deprecated_imports] failed:")
    for err in parse_errors:
        print(f"- {err}")
    raise SystemExit(1)

candidate_set = set(candidate_modules)
retired_set = set(retired_modules)
candidate_findings = {f for f in findings if f[2] in candidate_set}
retired_findings = {f for f in findings if f[2] in retired_set}

unexpected = sorted(candidate_findings - allowset)
stale = sorted(allowset - candidate_findings)

if unexpected or stale or retired_findings:
    print("[check_no_new_deprecated_imports] failed:")
    if retired_findings:
        print("- forbidden imports of retired deprecated modules:")
        for alias, rel_path, imported in sorted(retired_findings):
            print(f"  * {alias}|{rel_path}|{imported}")
    if unexpected:
        print("- unexpected candidate-phase deprecated imports (not in allowlist):")
        for alias, rel_path, imported in unexpected:
            print(f"  * {alias}|{rel_path}|{imported}")
    if stale:
        print("- stale allowlist entries (no longer needed for candidate-phase modules):")
        for alias, rel_path, imported in stale:
            print(f"  * {alias}|{rel_path}|{imported}")
    raise SystemExit(1)

print(
    "[check_no_new_deprecated_imports] passed: "
    f"candidate_modules={len(candidate_modules)}, retired_modules={len(retired_modules)}, "
    f"imports={len(findings)} across {len(repo_roots)} repo roots"
)
PY
