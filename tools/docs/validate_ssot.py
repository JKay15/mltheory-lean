#!/usr/bin/env python3
"""Validate docs/ssot/registry.json against fixed MLTheory SSOT contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "ssot" / "registry.json"
SCHEMA_PATH = ROOT / "docs" / "ssot" / "schema.json"

DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
MODULE_RE = re.compile(r"MLTheory(?:\.[A-Za-z0-9_.]+)?")

DECISION_STATUSES = {"locked", "active", "deprecated", "draft"}
MODULE_STATUSES = {"planned", "partial", "covered", "gap"}
GAP_STATUSES = {"planned", "partial", "covered", "gap"}
MODULE_SOURCES = {"mathlib", "slt", "external"}
MODULE_LAYERS = {"core", "methods", "applications", "books", "legacy"}
PROOF_STATUSES = {"placeholder", "statement", "proved"}
PLACEHOLDER_SCOPES = {"allowed", "forbidden"}
COVERAGE_STATUSES = {"planned", "partial", "covered", "gap"}
ALIAS_STATUSES = {"active", "deprecated"}


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"ERROR: file not found: {path}")
    except json.JSONDecodeError as err:
        raise SystemExit(f"ERROR: invalid JSON in {path}: {err}")


def _check_keys_exact(obj: dict, expected: set[str], label: str, errors: list[str]) -> None:
    actual = set(obj.keys())
    missing = expected - actual
    extra = actual - expected
    if missing:
        errors.append(f"{label}: missing keys: {sorted(missing)}")
    if extra:
        errors.append(f"{label}: extra keys: {sorted(extra)}")


def _check_date(value: str, label: str, errors: list[str]) -> None:
    if not DATE_RE.match(value):
        errors.append(f"{label}: invalid date format (expected YYYY-MM-DD): {value}")


def _iter_module_refs(text: str) -> Iterable[str]:
    return MODULE_RE.findall(text)


def validate_registry(data: object) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return (["root: must be an object"], warnings)

    top_keys = {"meta", "decisions", "modules", "gaps", "books", "aliases"}
    _check_keys_exact(data, top_keys, "root", errors)

    meta = data.get("meta")
    if not isinstance(meta, dict):
        errors.append("meta: must be an object")
    else:
        meta_keys = {"schema_version", "language", "toolchain", "last_updated", "policy"}
        _check_keys_exact(meta, meta_keys, "meta", errors)
        if isinstance(meta.get("last_updated"), str):
            _check_date(meta["last_updated"], "meta.last_updated", errors)
        else:
            errors.append("meta.last_updated: must be a string")
        if not isinstance(meta.get("policy"), list):
            errors.append("meta.policy: must be an array")

    decisions = data.get("decisions")
    if not isinstance(decisions, list):
        errors.append("decisions: must be an array")
    else:
        for i, row in enumerate(decisions):
            label = f"decisions[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(row, {"date", "decision", "status", "impact"}, label, errors)
            if isinstance(row.get("date"), str):
                _check_date(row["date"], f"{label}.date", errors)
            else:
                errors.append(f"{label}.date: must be a string")
            if row.get("status") not in DECISION_STATUSES:
                errors.append(f"{label}.status: invalid value: {row.get('status')}")

    modules = data.get("modules")
    module_paths: set[str] = set()
    if not isinstance(modules, list):
        errors.append("modules: must be an array")
    else:
        for i, row in enumerate(modules):
            label = f"modules[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(
                row,
                {
                    "module_path",
                    "domain",
                    "status",
                    "source",
                    "book_refs",
                    "layer",
                    "proof_status",
                    "placeholder_policy_scope",
                },
                label,
                errors,
            )
            module_path = row.get("module_path")
            if not isinstance(module_path, str) or not module_path:
                errors.append(f"{label}.module_path: must be a non-empty string")
            else:
                if module_path in module_paths:
                    errors.append(f"{label}.module_path: duplicate module_path: {module_path}")
                module_paths.add(module_path)
            if row.get("status") not in MODULE_STATUSES:
                errors.append(f"{label}.status: invalid value: {row.get('status')}")
            if row.get("source") not in MODULE_SOURCES:
                errors.append(f"{label}.source: invalid value: {row.get('source')}")
            layer = row.get("layer")
            if layer not in MODULE_LAYERS:
                errors.append(f"{label}.layer: invalid value: {layer}")
            proof_status = row.get("proof_status")
            if proof_status not in PROOF_STATUSES:
                errors.append(f"{label}.proof_status: invalid value: {proof_status}")
            placeholder_scope = row.get("placeholder_policy_scope")
            if placeholder_scope not in PLACEHOLDER_SCOPES:
                errors.append(
                    f"{label}.placeholder_policy_scope: invalid value: {placeholder_scope}"
                )

            if layer in {"core", "methods"} and placeholder_scope != "forbidden":
                errors.append(
                    f"{label}: core/methods modules must set "
                    "placeholder_policy_scope=forbidden"
                )
            if layer in {"applications", "books", "legacy"} and placeholder_scope != "allowed":
                warnings.append(
                    f"{label}: non-core layer usually uses "
                    "placeholder_policy_scope=allowed"
                )
            if placeholder_scope == "forbidden" and proof_status == "placeholder":
                errors.append(
                    f"{label}: placeholder policy is forbidden but proof_status is placeholder"
                )

    gaps = data.get("gaps")
    if not isinstance(gaps, list):
        errors.append("gaps: must be an array")
    else:
        for i, row in enumerate(gaps):
            label = f"gaps[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(
                row,
                {
                    "book",
                    "chapter",
                    "topic",
                    "status",
                    "last_search_date",
                    "sources_checked",
                    "candidate_repo",
                    "next_action",
                },
                label,
                errors,
            )
            if row.get("status") not in GAP_STATUSES:
                errors.append(f"{label}.status: invalid value: {row.get('status')}")
            if isinstance(row.get("last_search_date"), str):
                _check_date(row["last_search_date"], f"{label}.last_search_date", errors)
            else:
                errors.append(f"{label}.last_search_date: must be a string")
            if not str(row.get("next_action", "")).strip():
                errors.append(f"{label}.next_action: must be non-empty")

    books = data.get("books")
    if not isinstance(books, list):
        errors.append("books: must be an array")
    else:
        book_ids: set[str] = set()
        coverage_module_refs: set[str] = set()
        for i, row in enumerate(books):
            label = f"books[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(
                row,
                {"book_id", "title", "edition", "doc_file", "evidence_links", "coverage_rows"},
                label,
                errors,
            )
            book_id = row.get("book_id")
            if not isinstance(book_id, str) or not book_id:
                errors.append(f"{label}.book_id: must be a non-empty string")
            else:
                if book_id in book_ids:
                    errors.append(f"{label}.book_id: duplicate book_id: {book_id}")
                book_ids.add(book_id)
            if not isinstance(row.get("coverage_rows"), list):
                errors.append(f"{label}.coverage_rows: must be an array")
            else:
                for j, c in enumerate(row["coverage_rows"]):
                    clabel = f"{label}.coverage_rows[{j}]"
                    if not isinstance(c, dict):
                        errors.append(f"{clabel}: must be an object")
                        continue
                    _check_keys_exact(
                        c,
                        {"章节", "对应模块", "覆盖状态", "证据链接", "缺口说明", "后续动作"},
                        clabel,
                        errors,
                    )
                    if c.get("覆盖状态") not in COVERAGE_STATUSES:
                        errors.append(f"{clabel}.覆盖状态: invalid value: {c.get('覆盖状态')}")
                    for ref in _iter_module_refs(str(c.get("对应模块", ""))):
                        coverage_module_refs.add(ref)

        # Consistency check: every declared module appears in at least one book coverage row.
        # This is intentionally strict to keep docs navigable and prevent orphan module entries.
        missing_coverage = sorted(module_paths - coverage_module_refs)
        if missing_coverage:
            warnings.append(
                "coverage consistency: modules not referenced in any coverage_rows: "
                + ", ".join(missing_coverage)
            )

    aliases = data.get("aliases")
    if not isinstance(aliases, list):
        errors.append("aliases: must be an array")
    else:
        seen_legacy: set[str] = set()
        for i, row in enumerate(aliases):
            label = f"aliases[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(row, {"legacy_module", "canonical_module", "status"}, label, errors)
            legacy = row.get("legacy_module")
            canonical = row.get("canonical_module")
            if not isinstance(legacy, str) or not legacy:
                errors.append(f"{label}.legacy_module: must be a non-empty string")
            elif legacy in seen_legacy:
                errors.append(f"{label}.legacy_module: duplicate legacy module: {legacy}")
            else:
                seen_legacy.add(legacy)
            if not isinstance(canonical, str) or not canonical:
                errors.append(f"{label}.canonical_module: must be a non-empty string")
            if row.get("status") not in ALIAS_STATUSES:
                errors.append(f"{label}.status: invalid value: {row.get('status')}")

    return errors, warnings


def main() -> int:
    # Ensure schema exists and parses. Strict JSON-schema validation is optional;
    # this script enforces the repository's fixed contract directly.
    _ = _load_json(SCHEMA_PATH)
    data = _load_json(REGISTRY_PATH)

    errors, warnings = validate_registry(data)
    if errors:
        print("SSOT validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    if warnings:
        print("SSOT validation warnings:")
        for warning in warnings:
            print(f"- {warning}")

    print(
        "SSOT validation passed: "
        f"{len(data['decisions'])} decisions, "
        f"{len(data['modules'])} modules, "
        f"{len(data['gaps'])} gaps, "
        f"{len(data['books'])} books, "
        f"{len(data['aliases'])} aliases."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
