#!/usr/bin/env python3
"""Phase-0 audit for lean4 skill contract coverage.

This script audits the external lean4 skill without modifying it.
It reports coverage against a fixed 10-item matrix and emits
`native` (10/10) or `augmented` (<10) mode.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class AuditCheck:
    check_id: str
    title: str
    patterns: tuple[str, ...]
    files: tuple[str, ...]
    all_patterns_required: bool = True


DEFAULT_FILES = {
    "skill": Path("/Users/xiongjiangkai/.codex/skills/lean4/SKILL.md"),
    "cycle": Path("/Users/xiongjiangkai/.codex/skills/lean4/references/cycle-engine.md"),
    "axiom": Path("/Users/xiongjiangkai/.codex/skills/lean4/references/axiom-elimination.md"),
    "lsp_api": Path("/Users/xiongjiangkai/.codex/skills/lean4/references/lean-lsp-tools-api.md"),
}


CHECKS: tuple[AuditCheck, ...] = (
    AuditCheck(
        "build_gate",
        "构建门禁（lake build）",
        (r"\blake build\b",),
        ("skill", "cycle"),
    ),
    AuditCheck(
        "sorry_zero_gate",
        "sorry 清零门禁",
        (r"\bZero sorries\b|\bno sorries\b|\bzero sorries\b",),
        ("skill",),
        all_patterns_required=False,
    ),
    AuditCheck(
        "axiom_whitelist_gate",
        "自定义 axiom 白名单门禁",
        (r"standard axioms", r"Classical\.choice", r"propext", r"Quot\.sound"),
        ("skill", "axiom"),
    ),
    AuditCheck(
        "declaration_immutability",
        "定理声明不可私改规则",
        (r"Never change statements",),
        ("skill",),
    ),
    AuditCheck(
        "checkpoint_reproducible",
        "可复现 checkpoint 流程",
        (r"/lean4:checkpoint", r"build \+ axiom check \+ commit"),
        ("skill",),
    ),
    AuditCheck(
        "canonical_signature_lock",
        "canonical 入口签名锁定",
        (
            r"\bcanonical\b",
            r"\bsignature\b|\bsignatures\b",
            r"Never change statements|off-limits",
        ),
        ("skill",),
    ),
    AuditCheck(
        "dependency_closure_verifiable",
        "依赖闭包可验证（声明级）",
        (r"#print axioms", r"For individual theorems"),
        ("axiom",),
    ),
    AuditCheck(
        "intermediate_to_canonical_mapping",
        "中间概念到 canonical 映射约束",
        (r"\bintermediate\b", r"\bcanonical\b", r"mapping|bridge|traceability"),
        ("skill", "cycle"),
    ),
    AuditCheck(
        "official_toolchain_mapping",
        "官方工具链映射约束（Loogle/LeanSearch/InfoView/REPL）",
        (
            r"\bloogle\b",
            r"\bleansearch\b",
            r"\binfoview\b|\bloogleview\b",
            r"\brepl\b",
        ),
        ("skill", "lsp_api"),
    ),
    AuditCheck(
        "three_repo_boundary",
        "三仓边界约束",
        (
            r"paper-template",
            r"\bMLTheory\b",
            r"lean-proof-skills|skillpack",
            r"three[_ -]?repo|boundary",
        ),
        ("skill", "cycle"),
    ),
)


def _iter_matches(text: str, pattern: str) -> Iterable[tuple[int, str]]:
    regex = re.compile(pattern, re.IGNORECASE)
    for lineno, line in enumerate(text.splitlines(), start=1):
        if regex.search(line):
            yield lineno, line.strip()


def run_audit(file_map: dict[str, Path]) -> dict:
    missing_files = [key for key, path in file_map.items() if not path.exists()]
    if missing_files:
        return {
            "date": str(date.today()),
            "mode": "augmented",
            "score": "0/10",
            "status": "unavailable",
            "message": "missing lean4 skill files",
            "missing_files": [
                {"key": key, "path": str(file_map[key])} for key in missing_files
            ],
            "checks": [],
        }

    texts = {key: path.read_text(encoding="utf-8") for key, path in file_map.items()}
    check_results = []
    passed = 0

    for check in CHECKS:
        hits = []
        pattern_found = []
        for pat in check.patterns:
            found_for_pat = False
            for file_key in check.files:
                for line_no, line in _iter_matches(texts[file_key], pat):
                    hits.append(
                        {
                            "file_key": file_key,
                            "path": str(file_map[file_key]),
                            "line": line_no,
                            "snippet": line[:180],
                            "pattern": pat,
                        }
                    )
                    found_for_pat = True
                    break
                if found_for_pat:
                    break
            pattern_found.append(found_for_pat)

        ok = all(pattern_found) if check.all_patterns_required else any(pattern_found)
        if ok:
            passed += 1
        check_results.append(
            {
                "check_id": check.check_id,
                "title": check.title,
                "passed": ok,
                "hits": hits[:4],
            }
        )

    mode = "native" if passed == len(CHECKS) else "augmented"
    return {
        "date": str(date.today()),
        "mode": mode,
        "score": f"{passed}/{len(CHECKS)}",
        "status": "ok",
        "files": {key: str(path) for key, path in file_map.items()},
        "checks": check_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit lean4 contract coverage.")
    parser.add_argument(
        "--write-json",
        type=Path,
        help="Optional output path for JSON report (e.g. docs/ssot/lean4_contract_audit.json)",
    )
    args = parser.parse_args()

    report = run_audit(DEFAULT_FILES)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)

    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(text + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
