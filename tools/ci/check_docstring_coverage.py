#!/usr/bin/env python3
"""Draft gate: report Core/Methods declaration docstring coverage.

Default mode is non-blocking and reports coverage stats plus missing entries.
Set --strict (or STRICT_CORE_DOCSTRING_COVERAGE=1) to enforce min coverage.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET_DIRS = (ROOT / "MLTheory" / "Core", ROOT / "MLTheory" / "Methods")
DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]+\]\s*)*"
    r"(?:(?:private|protected|noncomputable|unsafe|partial|scoped)\s+)*"
    r"(def|theorem|lemma|abbrev|structure|class|inductive|instance)\s+([A-Za-z0-9_'.]+)"
)


@dataclass
class MissingDoc:
    file: Path
    line: int
    kind: str
    name: str


def _has_docstring(lines: list[str], index: int) -> bool:
    i = index - 1
    while i >= 0:
        s = lines[i].strip()
        if not s:
            i -= 1
            continue
        if s.startswith("@[") or s.startswith("attribute ["):
            i -= 1
            continue
        break
    if i < 0:
        return False

    cur = lines[i].strip()
    if cur.startswith("/--"):
        return True
    if not cur.endswith("-/"):
        return False

    # Multi-line comment: walk up to find doc-comment start.
    j = i
    while j >= 0:
        s = lines[j].strip()
        if "/--" in s:
            return True
        if s.startswith("/-") and not s.startswith("/--"):
            return False
        j -= 1
    return False


def collect_missing() -> tuple[int, int, list[MissingDoc]]:
    total = 0
    documented = 0
    missing: list[MissingDoc] = []

    files: list[Path] = []
    for directory in TARGET_DIRS:
        files.extend(sorted(directory.rglob("*.lean")))

    for file in files:
        lines = file.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines):
            m = DECL_RE.match(line)
            if not m:
                continue
            kind, name = m.group(1), m.group(2)
            total += 1
            if _has_docstring(lines, idx):
                documented += 1
                continue
            missing.append(MissingDoc(file=file, line=idx + 1, kind=kind, name=name))

    return total, documented, missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Core/Methods docstring coverage.")
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=0.70,
        help="minimum required coverage ratio in strict mode (0.0-1.0)",
    )
    parser.add_argument(
        "--report-limit",
        type=int,
        default=80,
        help="max missing declarations to print",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail when coverage is below --min-coverage",
    )
    args = parser.parse_args()

    strict = args.strict or os.getenv("STRICT_CORE_DOCSTRING_COVERAGE") == "1"
    if not (0.0 <= args.min_coverage <= 1.0):
        print("[check_docstring_coverage] --min-coverage must be in [0, 1].")
        return 2

    total, documented, missing = collect_missing()
    if total == 0:
        print("[check_docstring_coverage] no declarations found under Core/Methods.")
        return 0

    coverage = documented / total
    print(
        "[check_docstring_coverage] "
        f"documented={documented} total={total} coverage={coverage:.2%} "
        f"missing={len(missing)} strict={strict}"
    )
    if missing:
        print("[check_docstring_coverage] missing docstrings (sample):")
        for row in missing[: args.report_limit]:
            rel = row.file.relative_to(ROOT)
            print(f"- {rel}:{row.line}: {row.kind} {row.name}")
        if len(missing) > args.report_limit:
            print(
                f"- ... {len(missing) - args.report_limit} additional entries omitted "
                f"(increase --report-limit to show more)."
            )

    if strict and coverage < args.min_coverage:
        print(
            "[check_docstring_coverage] failed: "
            f"coverage {coverage:.2%} < required {args.min_coverage:.2%}"
        )
        return 1
    if not strict:
        print(
            "[check_docstring_coverage] draft mode: non-blocking report. "
            "Use --strict (or STRICT_CORE_DOCSTRING_COVERAGE=1) to enforce."
        )
    else:
        print("[check_docstring_coverage] passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
