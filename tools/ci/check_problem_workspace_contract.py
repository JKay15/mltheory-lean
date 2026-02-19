#!/usr/bin/env python3
"""Validate Problems workspace contract and generated proof-map sync."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBLEMS_ROOT = ROOT / "Problems"
PROOF_MAP_INDEX = ROOT / "docs" / "_auto" / "proof_maps.json"
REQUIRED_FILES = (
    "Spec.lean",
    "Cache.lean",
    "Proof.lean",
    "Tasks.yaml",
    "Sources.md",
    "Glossary.yaml",
)


def collect_problem_dirs() -> list[Path]:
    if not PROBLEMS_ROOT.exists():
        return []
    out: list[Path] = []
    for spec in PROBLEMS_ROOT.rglob("Spec.lean"):
        parent = spec.parent
        rel = parent.relative_to(PROBLEMS_ROOT)
        if len(rel.parts) != 2:
            continue
        out.append(parent)
    out.sort()
    return out


def file_has_token(path: Path, pattern: re.Pattern[str]) -> bool:
    text = path.read_text(encoding="utf-8")
    return pattern.search(text) is not None


def check_no_sketch_imports(errors: list[str]) -> None:
    cmd = [
        "rg",
        "-n",
        r"^\s*import\s+Problems\..*Sketch",
        str(ROOT / "MLTheory"),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError as err:
        errors.append(f"failed to run rg for sketch import check: {err}")
        return
    if proc.returncode == 0 and proc.stdout.strip():
        for line in proc.stdout.strip().splitlines():
            errors.append(f"Sketch import is forbidden in MLTheory tree: {line}")
    elif proc.returncode not in (0, 1):
        errors.append(f"rg sketch import check failed: code={proc.returncode}")


def load_proof_map_index(errors: list[str]) -> dict:
    if not PROOF_MAP_INDEX.exists():
        errors.append(f"missing file: {PROOF_MAP_INDEX.relative_to(ROOT)}")
        return {}
    try:
        data = json.loads(PROOF_MAP_INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        errors.append(f"{PROOF_MAP_INDEX.relative_to(ROOT)} invalid JSON: {err}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{PROOF_MAP_INDEX.relative_to(ROOT)} root must be JSON object")
        return {}
    return data


def main() -> int:
    errors: list[str] = []
    problem_dirs = collect_problem_dirs()
    if not problem_dirs:
        print("[check_problem_workspace_contract] no Problems/*/*/Spec.lean found; skip.")
        return 0

    sorry_pat = re.compile(r"\bsorry\b")
    axiom_pat = re.compile(r"\baxiom\b")

    expected_ids: set[str] = set()
    for pdir in problem_dirs:
        rel = pdir.relative_to(ROOT)
        suite = rel.parts[1]
        problem = rel.parts[2]
        problem_id = f"{suite}/{problem}"
        expected_ids.add(problem_id)

        for fname in REQUIRED_FILES:
            if not (pdir / fname).exists():
                errors.append(f"{rel}/{fname} missing")

        spec_path = pdir / "Spec.lean"
        cache_path = pdir / "Cache.lean"
        if spec_path.exists():
            if file_has_token(spec_path, sorry_pat):
                errors.append(f"{spec_path.relative_to(ROOT)} must not contain `sorry`")
            if file_has_token(spec_path, axiom_pat):
                errors.append(f"{spec_path.relative_to(ROOT)} must not contain `axiom`")
        if cache_path.exists():
            if file_has_token(cache_path, sorry_pat):
                errors.append(f"{cache_path.relative_to(ROOT)} must not contain `sorry`")
            if file_has_token(cache_path, axiom_pat):
                errors.append(f"{cache_path.relative_to(ROOT)} must not contain `axiom`")

        proof_map = pdir / "ProofMap.json"
        if not proof_map.exists():
            errors.append(f"{proof_map.relative_to(ROOT)} missing (run tools/index/gen_proof_map.py)")
        else:
            try:
                payload = json.loads(proof_map.read_text(encoding="utf-8"))
            except json.JSONDecodeError as err:
                errors.append(f"{proof_map.relative_to(ROOT)} invalid JSON: {err}")
                payload = {}
            if isinstance(payload, dict):
                got_id = payload.get("problem_id")
                if got_id != problem_id:
                    errors.append(
                        f"{proof_map.relative_to(ROOT)} problem_id mismatch: expected {problem_id}, got {got_id}"
                    )
                if not isinstance(payload.get("nodes"), list) or not isinstance(
                    payload.get("edges"), list
                ):
                    errors.append(
                        f"{proof_map.relative_to(ROOT)} must contain list fields `nodes` and `edges`"
                    )

    check_no_sketch_imports(errors)

    index = load_proof_map_index(errors)
    index_ids: set[str] = set()
    if isinstance(index.get("problems"), list):
        for i, row in enumerate(index["problems"]):
            if not isinstance(row, dict):
                errors.append(f"proof_maps.json problems[{i}] must be object")
                continue
            pid = row.get("id")
            if not isinstance(pid, str) or not pid:
                errors.append(f"proof_maps.json problems[{i}] missing non-empty `id`")
                continue
            index_ids.add(pid)
            map_path = row.get("proof_map")
            if not isinstance(map_path, str) or not map_path:
                errors.append(f"proof_maps.json problems[{i}] missing `proof_map`")
                continue
            rel = map_path[2:] if map_path.startswith("./") else map_path
            if rel.startswith("_auto/"):
                full = ROOT / "docs" / rel
            else:
                full = ROOT / rel
            if not full.exists():
                errors.append(f"proof_maps.json points to missing file: {rel}")
    else:
        errors.append("proof_maps.json missing list field `problems`")

    missing_in_index = sorted(expected_ids - index_ids)
    if missing_in_index:
        errors.append(
            "proof_maps.json missing problem ids: " + ", ".join(missing_in_index)
        )

    if errors:
        print("[check_problem_workspace_contract] failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print(
        "[check_problem_workspace_contract] passed "
        f"(problems={len(problem_dirs)}, indexed={len(index_ids)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
