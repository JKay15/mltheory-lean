#!/usr/bin/env python3
"""Generate mathlib structure artifacts and MLTheory->mathlib slice.

Outputs (under artifacts/index by default):
  - mathlib_modules.json
  - mathlib_imports.json
  - mathlib_hubs.json
  - mathlib_aggregators.json
  - mathlib_slice.json
  - mltheory_to_mathlib.json

This script is code-first and deterministic:
  - locate mathlib from lake-manifest.json (no hard-coded paths)
  - parse import lines from Lean source files
  - compute direct + transitive MLTheory->mathlib dependency slice
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ModuleFile:
    module: str
    path: Path


def is_mathlib_module(module: str) -> bool:
    return module == "Mathlib" or module.startswith("Mathlib.")


def utc_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_manifest(repo_root: Path) -> dict:
    manifest_path = repo_root / "lake-manifest.json"
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as err:
        raise SystemExit(f"missing file: {manifest_path}") from err
    except json.JSONDecodeError as err:
        raise SystemExit(f"invalid JSON in {manifest_path}: {err}") from err


def find_mathlib_dir(repo_root: Path, manifest: dict) -> Path:
    packages = manifest.get("packages", [])
    if not isinstance(packages, list):
        raise SystemExit("lake-manifest.json: `packages` must be a list")

    mathlib_pkg = None
    for pkg in packages:
        if isinstance(pkg, dict) and pkg.get("name") == "mathlib":
            mathlib_pkg = pkg
            break
    if mathlib_pkg is None:
        raise SystemExit("lake-manifest.json: missing package `mathlib`")

    raw_dir = mathlib_pkg.get("dir")
    if isinstance(raw_dir, str) and raw_dir.strip():
        candidate = Path(raw_dir)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
    else:
        packages_dir = manifest.get("packagesDir", ".lake/packages")
        if not isinstance(packages_dir, str) or not packages_dir.strip():
            packages_dir = ".lake/packages"
        candidate = repo_root / packages_dir / "mathlib"

    candidate = candidate.resolve()
    if not candidate.exists():
        raise SystemExit(f"mathlib dir not found: {candidate}")
    if not (candidate / "Mathlib").exists():
        raise SystemExit(f"mathlib source root missing: {candidate / 'Mathlib'}")
    return candidate


def module_name(repo_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(repo_root).with_suffix("")
    return ".".join(rel.parts)


def iter_mltheory_modules(repo_root: Path) -> list[ModuleFile]:
    files: list[Path] = []
    root_entry = repo_root / "MLTheory.lean"
    if root_entry.exists():
        files.append(root_entry)
    files.extend(sorted((repo_root / "MLTheory").rglob("*.lean")))

    out: list[ModuleFile] = []
    for file_path in files:
        out.append(ModuleFile(module=module_name(repo_root, file_path), path=file_path))
    return out


def iter_mathlib_modules(repo_root: Path, mathlib_dir: Path) -> list[ModuleFile]:
    files: list[Path] = []
    root_entry = mathlib_dir / "Mathlib.lean"
    if root_entry.exists():
        files.append(root_entry)
    files.extend(sorted((mathlib_dir / "Mathlib").rglob("*.lean")))

    out: list[ModuleFile] = []
    for file_path in files:
        out.append(ModuleFile(module=module_name(mathlib_dir, file_path), path=file_path))
    return out


def parse_imports(file_path: Path) -> list[str]:
    imports: list[str] = []
    for raw in file_path.read_text(encoding="utf-8").splitlines():
        line = raw.split("--", 1)[0].strip()
        if not line:
            continue

        tail: str | None = None
        if line.startswith("import "):
            tail = line[len("import ") :].strip()
        elif line.startswith("public import "):
            tail = line[len("public import ") :].strip()
        elif line.startswith("private import "):
            tail = line[len("private import ") :].strip()

        if tail is None:
            continue
        if not tail:
            continue
        tokens = tail.split()
        if tokens and tokens[0] == "all":
            tokens = tokens[1:]
        imports.extend(tokens)
    return imports


def unique_edges(edges: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for edge in edges:
        if edge in seen:
            continue
        seen.add(edge)
        out.append(edge)
    return out


def compute_fan_stats(edges: Iterable[tuple[str, str]]) -> tuple[dict[str, int], dict[str, int]]:
    fan_in: dict[str, int] = defaultdict(int)
    fan_out: dict[str, int] = defaultdict(int)
    for src, dst in edges:
        fan_out[src] += 1
        fan_in[dst] += 1
    return dict(fan_in), dict(fan_out)


def top_modules(
    modules: list[str],
    fan_in: dict[str, int],
    fan_out: dict[str, int],
    key: str,
    k: int,
) -> list[dict]:
    if key == "fan_in":
        ranked = sorted(
            modules,
            key=lambda m: (-fan_in.get(m, 0), -fan_out.get(m, 0), m),
        )
    else:
        ranked = sorted(
            modules,
            key=lambda m: (-fan_out.get(m, 0), -fan_in.get(m, 0), m),
        )
    out: list[dict] = []
    for module in ranked[:k]:
        out.append(
            {
                "module": module,
                "fan_in": fan_in.get(module, 0),
                "fan_out": fan_out.get(module, 0),
            }
        )
    return out


def detect_aggregators(
    modules: list[str],
    fan_in: dict[str, int],
    fan_out: dict[str, int],
    top_k: int,
) -> list[dict]:
    by_fan_out = sorted(modules, key=lambda m: (-fan_out.get(m, 0), -fan_in.get(m, 0), m))
    top_by_fan_out = set(by_fan_out[: top_k * 4])
    out: list[dict] = []

    for module in sorted(modules):
        name = module.split(".")[-1]
        reason: list[str] = []
        if module == "Mathlib":
            reason.append("top_entry")
        if name in {"Basic", "All", "Init"}:
            reason.append(f"name={name}")
        if module in top_by_fan_out and fan_out.get(module, 0) > 0:
            reason.append("high_fan_out")
        if not reason:
            continue
        out.append(
            {
                "module": module,
                "fan_in": fan_in.get(module, 0),
                "fan_out": fan_out.get(module, 0),
                "reason": reason,
            }
        )

    out.sort(key=lambda row: (-row["fan_out"], -row["fan_in"], row["module"]))
    return out[:top_k]


def compute_slice(
    ml_edges: list[tuple[str, str]],
    math_edges: list[tuple[str, str]],
    ml_modules: list[str],
) -> tuple[dict[str, dict[str, list[str]]], list[str], list[str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for src, dst in math_edges:
        if is_mathlib_module(src) and is_mathlib_module(dst):
            adjacency[src].append(dst)

    for key in adjacency:
        adjacency[key] = sorted(set(adjacency[key]))

    direct: dict[str, set[str]] = {m: set() for m in ml_modules}
    for src, dst in ml_edges:
        if not src.startswith("MLTheory"):
            continue
        if is_mathlib_module(dst):
            direct.setdefault(src, set()).add(dst)

    def closure(starts: set[str]) -> set[str]:
        seen = set(starts)
        q = deque(starts)
        while q:
            node = q.popleft()
            for nxt in adjacency.get(node, []):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        return seen

    mapping: dict[str, dict[str, list[str]]] = {}
    roots_union: set[str] = set()
    slice_union: set[str] = set()
    for module in sorted(ml_modules):
        roots = direct.get(module, set())
        clo = closure(roots)
        roots_union |= roots
        slice_union |= clo
        mapping[module] = {
            "direct": sorted(roots),
            "closure": sorted(clo),
        }

    return mapping, sorted(roots_union), sorted(slice_union)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate MLTheory->mathlib structure artifacts")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd(), help="MLTheory repo root")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("artifacts/index"),
        help="Output directory (default: artifacts/index)",
    )
    ap.add_argument("--top-k", type=int, default=50, help="Top-K used for hubs/aggregators")
    args = ap.parse_args()

    repo_root = args.repo_root.resolve()
    out_dir = args.out_dir if args.out_dir.is_absolute() else (repo_root / args.out_dir)
    out_dir = out_dir.resolve()
    generated_at = utc_date()

    manifest = load_manifest(repo_root)
    mathlib_dir = find_mathlib_dir(repo_root, manifest)

    ml_modules_info = iter_mltheory_modules(repo_root)
    math_modules_info = iter_mathlib_modules(repo_root, mathlib_dir)

    ml_edges_raw: list[tuple[str, str]] = []
    for row in ml_modules_info:
        for dst in parse_imports(row.path):
            ml_edges_raw.append((row.module, dst))
    ml_edges = unique_edges(ml_edges_raw)

    math_edges_raw: list[tuple[str, str]] = []
    for row in math_modules_info:
        for dst in parse_imports(row.path):
            math_edges_raw.append((row.module, dst))
    math_edges = unique_edges(math_edges_raw)

    math_modules = sorted(row.module for row in math_modules_info)
    fan_in, fan_out = compute_fan_stats(math_edges)

    top_fan_in = top_modules(math_modules, fan_in, fan_out, "fan_in", args.top_k)
    top_fan_out = top_modules(math_modules, fan_in, fan_out, "fan_out", args.top_k)
    aggregators = detect_aggregators(math_modules, fan_in, fan_out, args.top_k)

    mapping, roots, slice_modules = compute_slice(
        ml_edges=ml_edges,
        math_edges=math_edges,
        ml_modules=sorted(row.module for row in ml_modules_info),
    )

    modules_payload = {
        "generated_at": generated_at,
        "package": "mathlib",
        "mathlib_dir": str(mathlib_dir),
        "count": len(math_modules_info),
        "modules": [
            {
                "module": row.module,
                "path": str(row.path.relative_to(mathlib_dir)),
                "layer": "mathlib",
                "package": "mathlib",
            }
            for row in sorted(math_modules_info, key=lambda x: x.module)
        ],
    }
    write_json(out_dir / "mathlib_modules.json", modules_payload)

    imports_payload = {
        "generated_at": generated_at,
        "package": "mathlib",
        "nodes": math_modules,
        "edges": [
            {"src": src, "dst": dst, "type": "imports", "package": "mathlib"}
            for src, dst in sorted(math_edges)
        ],
    }
    write_json(out_dir / "mathlib_imports.json", imports_payload)

    hubs_payload = {
        "generated_at": generated_at,
        "package": "mathlib",
        "top_k": args.top_k,
        "top_by_fan_in": top_fan_in,
        "top_by_fan_out": top_fan_out,
    }
    write_json(out_dir / "mathlib_hubs.json", hubs_payload)

    aggregators_payload = {
        "generated_at": generated_at,
        "package": "mathlib",
        "top_k": args.top_k,
        "aggregators": aggregators,
    }
    write_json(out_dir / "mathlib_aggregators.json", aggregators_payload)

    slice_payload = {
        "generated_at": generated_at,
        "package": "mathlib",
        "root_direct_imports": roots,
        "slice": slice_modules,
        "size": len(slice_modules),
    }
    write_json(out_dir / "mathlib_slice.json", slice_payload)

    mapping_payload = {
        "generated_at": generated_at,
        "mltheory_module_count": len(mapping),
        "mapping": mapping,
    }
    write_json(out_dir / "mltheory_to_mathlib.json", mapping_payload)

    print(f"[generate_mathlib_slice] repo_root={repo_root}")
    print(f"[generate_mathlib_slice] mathlib_dir={mathlib_dir}")
    print(f"[generate_mathlib_slice] wrote outputs to {out_dir}")
    print(
        "[generate_mathlib_slice] stats: "
        f"ml_modules={len(ml_modules_info)}, math_modules={len(math_modules_info)}, "
        f"math_edges={len(math_edges)}, slice_size={len(slice_modules)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
