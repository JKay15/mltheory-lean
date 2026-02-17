#!/usr/bin/env python3
"""Check SSOT text surfaces for deprecated alias references and duplicate coverage refs."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"
MODULE_RE = re.compile(r"MLTheory(?:\.[A-Za-z0-9_]+)+")


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    aliases = data.get("aliases", [])
    books = data.get("books", [])
    gaps = data.get("gaps", [])

    deprecated_alias_map = {
        str(a.get("legacy_module")): str(a.get("canonical_module"))
        for a in aliases
        if isinstance(a, dict) and a.get("status") == "deprecated"
    }

    errors: list[str] = []
    coverage_rows_scanned = 0
    gap_rows_scanned = 0

    for b_idx, book in enumerate(books):
        book_id = str(book.get("book_id", f"books[{b_idx}]"))
        for r_idx, row in enumerate(book.get("coverage_rows", [])):
            chapter = str(row.get("章节", f"coverage_rows[{r_idx}]"))
            refs_text = str(row.get("对应模块", ""))
            refs = MODULE_RE.findall(refs_text)
            coverage_rows_scanned += 1

            seen: list[str] = []
            duplicate_refs: list[str] = []
            for ref in refs:
                if ref in seen and ref not in duplicate_refs:
                    duplicate_refs.append(ref)
                seen.append(ref)
            if duplicate_refs:
                errors.append(
                    f"{book_id}/{chapter}: duplicate module refs in 覆盖表: {', '.join(duplicate_refs)}"
                )

            deprecated_hits = sorted({ref for ref in refs if ref in deprecated_alias_map})
            if deprecated_hits:
                hints = "; ".join(f"{h} -> {deprecated_alias_map[h]}" for h in deprecated_hits)
                errors.append(
                    f"{book_id}/{chapter}: 覆盖表引用了 deprecated alias: {', '.join(deprecated_hits)} "
                    f"(建议: {hints})"
                )

    for g_idx, gap in enumerate(gaps):
        label = f"{gap.get('book', 'gaps')}/{gap.get('chapter', g_idx)}"
        topic = str(gap.get("topic", ""))
        next_action = str(gap.get("next_action", ""))
        refs = MODULE_RE.findall(topic + " " + next_action)
        gap_rows_scanned += 1
        deprecated_hits = sorted({ref for ref in refs if ref in deprecated_alias_map})
        if deprecated_hits:
            hints = "; ".join(f"{h} -> {deprecated_alias_map[h]}" for h in deprecated_hits)
            errors.append(
                f"{label}: GapLedger topic/next_action 引用了 deprecated alias: "
                f"{', '.join(deprecated_hits)} (建议: {hints})"
            )

    if errors:
        print("[check_registry_reference_hygiene] failed:")
        for e in errors:
            print(f"- {e}")
        return 1

    print(
        "[check_registry_reference_hygiene] passed: "
        f"coverage_rows={coverage_rows_scanned}, gaps={gap_rows_scanned}, "
        f"deprecated_aliases={len(deprecated_alias_map)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

