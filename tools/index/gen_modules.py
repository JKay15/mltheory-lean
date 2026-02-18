#!/usr/bin/env python3
"""Generate a code-first Lean module index."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def infer_layer(module: str) -> str:
    if module.startswith("MLTheory.Core."):
        return "core"
    if module.startswith("MLTheory.Methods."):
        return "methods"
    if module.startswith("MLTheory.Applications."):
        return "applications"
    if module.startswith("MLTheory.Books."):
        return "books"
    if module.startswith("Mathlib."):
        return "mathlib"
    return "other"


def parse_imports(lines: list[str]) -> list[str]:
    imports: set[str] = set()
    for raw in lines:
        line = raw.split("--", 1)[0].strip()
        if not line.startswith("import "):
            continue
        tail = line[len("import ") :].strip()
        if not tail:
            continue
        for mod in tail.split():
            imports.add(mod)
    return sorted(imports)


def parse_doc_title(lines: list[str]) -> str | None:
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("/-!"):
            title = line[3:].strip()
            if title.endswith("-/"):
                title = title[:-2].strip()
            return title or None
        if not line.startswith("--"):
            break
    return None


def module_name(src_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(src_root.parent).with_suffix("")
    return ".".join(rel.parts)


def relative_path(root: Path, file_path: Path) -> str:
    try:
        return str(file_path.relative_to(root))
    except ValueError:
        return str(file_path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    ap.add_argument(
        "--src",
        type=Path,
        action="append",
        required=True,
        help="Lean source root (repeatable)",
    )
    ap.add_argument("--out", type=Path, required=True, help="Output JSON path")
    ap.add_argument(
        "--package",
        type=str,
        default="MLTheory",
        help="Package label: MLTheory|mathlib|std|other",
    )
    args = ap.parse_args()

    root = args.root.resolve()
    src_roots = [src.resolve() for src in args.src]
    out = args.out.resolve()

    records: list[dict] = []
    seen_modules: set[str] = set()
    for src in src_roots:
        if not src.exists():
            continue
        for lean_file in sorted(src.rglob("*.lean")):
            lines = lean_file.read_text(encoding="utf-8").splitlines()
            mod = module_name(src, lean_file)
            if mod in seen_modules:
                continue
            seen_modules.add(mod)
            doc_title = parse_doc_title(lines)
            rec = {
                "module": mod,
                "path": relative_path(root, lean_file),
                "layer": infer_layer(mod),
                "imports": parse_imports(lines),
                "package": args.package,
            }
            if doc_title:
                rec["doc_title"] = doc_title
            records.append(rec)

    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": str(date.today()),
        "package": args.package,
        "module_count": len(records),
        "modules": records,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[gen_modules] wrote {out} ({len(records)} modules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
