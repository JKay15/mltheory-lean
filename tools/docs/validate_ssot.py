#!/usr/bin/env python3
"""Validate docs/ssot/registry.json against taxonomy v2 SSOT contract."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "ssot" / "registry.json"
SCHEMA_PATH = ROOT / "docs" / "ssot" / "schema.json"

DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
COMPAT_RELEASE_WINDOW_RE = re.compile(r"^([0-9]+)\s+release(?:s)?$")
MODULE_RE = re.compile(r"MLTheory(?:\.[A-Za-z0-9_.]+)?")

DECISION_STATUSES = {"locked", "active", "deprecated", "draft"}
NODE_TIERS = {"foundation", "methods", "application", "support"}
NODE_STATUSES = {"active", "planned", "deprecated"}
RELATION_TYPES = {"secondary_parent", "related"}
WORKFLOW_STATUSES = {"active", "planned", "deprecated"}
OFFICIAL_CAPABILITIES_REQUIRED = {"Loogle", "LeanSearch", "InfoView/LoogleView", "REPL"}

CANONICAL_SPEC_STATUSES = {"active", "deprecated", "draft"}
AXIOM_POLICIES = {"standard_only", "allowlisted"}

MODULE_STATUSES = {"planned", "partial", "covered", "gap"}
MODULE_SOURCES = {"mathlib", "slt", "external"}
MODULE_LAYERS = {"core", "methods", "applications", "books", "legacy"}
PROOF_STATUSES = {"placeholder", "statement", "proved"}
PLACEHOLDER_SCOPES = {"allowed", "forbidden"}
MODULE_ROLES = {"canonical", "compat", "bridge", "tool", "placeholder"}
USER_SURFACES = {"public", "internal"}
SOURCE_TRACKS = {"native", "books", "legacy"}
PLANNED_SOURCE_TRACKS = {"native", "books"}
EXECUTION_HORIZONS = {"near", "mid", "far"}
EXECUTION_PRIORITIES = {"P1", "P2", "P3"}
CLEANUP_PRIORITIES = {"P1", "P2", "P3"}
CLEANUP_BATCH_RE = re.compile(r"^B[1-9][0-9]*$")
CLEANUP_EXECUTION_STATES = {"pending", "deprecated_announced", "migrating", "ready_to_remove"}
CLEANUP_TRANSIENT_POLICY_PATTERNS = (
    re.compile(r"^cleanup_b[1-9][0-9]*_pending$"),
    re.compile(r"^cleanup_b[1-9][0-9]*_deprecated_announced$"),
    re.compile(r"^cleanup_b[1-9][0-9]*_migrating$"),
    re.compile(r"^cleanup_b[1-9][0-9]*_ready_to_remove$"),
    re.compile(r"^cleanup_b[1-9][0-9]*_[a-z0-9]+_deprecated_announced$"),
    re.compile(r"^active_aliases_phase2_batching$"),
    re.compile(r"^cleanup_candidates_migrating$"),
)

GAP_STATUSES = {"planned", "partial", "covered", "gap"}
COVERAGE_STATUSES = {"planned", "partial", "covered", "gap"}
ALIAS_STATUSES = {"active", "deprecated"}
PLANNED_PARTIAL_REASON_EVIDENCE_TOKENS = (
    "external",
    "source_url",
    "candidate_repo",
    "github",
    "mathlib",
    "evidence",
    "evidence",
    "candidate",
    "source",
)


LEGACY_DOMAIN_BANNED_PATTERNS = [
    re.compile(r"\bIndex\b", re.IGNORECASE),
    re.compile(r"\bTheory\b", re.IGNORECASE),
    re.compile(r"\bRoot\b", re.IGNORECASE),
    re.compile(r"\bOperations\s+Research\b", re.IGNORECASE),
    re.compile(r"\bML\s+Theory\b", re.IGNORECASE),
]


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


def _module_file_path(module_path: str) -> Path:
    if module_path == "MLTheory":
        return ROOT / "MLTheory.lean"
    return ROOT / f"{module_path.replace('.', '/')}.lean"


def _planned_partial_reason_has_evidence(reason: str) -> bool:
    lowered = reason.lower()
    if "no local .lean file yet" in lowered:
        return False
    return any(tok in lowered for tok in PLANNED_PARTIAL_REASON_EVIDENCE_TOKENS)


def validate_registry(data: object) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    policy_tags: list[str] = []

    if not isinstance(data, dict):
        return (["root: must be an object"], warnings)

    top_keys = {
        "meta",
        "decisions",
        "taxonomy_nodes",
        "taxonomy_relations",
        "official_workflow_refs",
        "canonical_specs",
        "modules",
        "planned_modules",
        "execution_backlog",
        "structure_cleanup_candidates",
        "gaps",
        "books",
        "aliases",
    }
    _check_keys_exact(data, top_keys, "root", errors)

    meta = data.get("meta")
    cleanup_release_epoch: int | None = None
    if not isinstance(meta, dict):
        errors.append("meta: must be an object")
    else:
        meta_keys = {
            "schema_version",
            "language",
            "toolchain",
            "last_updated",
            "cleanup_release_epoch",
            "policy",
        }
        _check_keys_exact(meta, meta_keys, "meta", errors)
        if isinstance(meta.get("last_updated"), str):
            _check_date(meta["last_updated"], "meta.last_updated", errors)
        else:
            errors.append("meta.last_updated: must be a string")
        if isinstance(meta.get("cleanup_release_epoch"), int) and meta["cleanup_release_epoch"] >= 1:
            cleanup_release_epoch = int(meta["cleanup_release_epoch"])
        else:
            errors.append("meta.cleanup_release_epoch: must be integer >= 1")
        if not isinstance(meta.get("policy"), list):
            errors.append("meta.policy: must be an array")
        else:
            raw_policy = meta["policy"]
            if not all(isinstance(tag, str) and tag.strip() for tag in raw_policy):
                errors.append("meta.policy: all entries must be non-empty strings")
            else:
                policy_tags = list(raw_policy)

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

    taxonomy_nodes = data.get("taxonomy_nodes")
    node_ids: set[str] = set()
    parent_map: dict[str, str | None] = {}
    if not isinstance(taxonomy_nodes, list):
        errors.append("taxonomy_nodes: must be an array")
    else:
        for i, row in enumerate(taxonomy_nodes):
            label = f"taxonomy_nodes[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(
                row,
                {"node_id", "name", "tier", "primary_parent_id", "status", "order"},
                label,
                errors,
            )
            node_id = row.get("node_id")
            parent_id = row.get("primary_parent_id")
            if not isinstance(node_id, str) or not node_id.strip():
                errors.append(f"{label}.node_id: must be a non-empty string")
                continue
            if node_id in node_ids:
                errors.append(f"{label}.node_id: duplicate node_id `{node_id}`")
            node_ids.add(node_id)
            parent_map[node_id] = parent_id if isinstance(parent_id, str) else None

            if row.get("tier") not in NODE_TIERS:
                errors.append(f"{label}.tier: invalid value: {row.get('tier')}")
            if row.get("status") not in NODE_STATUSES:
                errors.append(f"{label}.status: invalid value: {row.get('status')}")
            if not isinstance(row.get("order"), int):
                errors.append(f"{label}.order: must be integer")
            if not isinstance(row.get("name"), str) or not row.get("name", "").strip():
                errors.append(f"{label}.name: must be non-empty string")

        roots = [n for n, p in parent_map.items() if p is None]
        if len(roots) != 1:
            errors.append(f"taxonomy_nodes: expected exactly 1 root, got {len(roots)}")

        for node_id, parent_id in parent_map.items():
            if parent_id is not None and parent_id not in node_ids:
                errors.append(f"taxonomy_nodes: `{node_id}` references missing parent `{parent_id}`")

        # cycle check on primary parent chain
        visiting: set[str] = set()
        visited: set[str] = set()

        def dfs(node: str) -> None:
            if node in visiting:
                errors.append(f"taxonomy_nodes: cycle detected at `{node}`")
                return
            if node in visited:
                return
            visiting.add(node)
            parent = parent_map.get(node)
            if parent is not None:
                dfs(parent)
            visiting.remove(node)
            visited.add(node)

        for node in sorted(node_ids):
            dfs(node)

    taxonomy_relations = data.get("taxonomy_relations")
    if not isinstance(taxonomy_relations, list):
        errors.append("taxonomy_relations: must be an array")
    else:
        seen_rel: set[tuple[str, str, str]] = set()
        for i, row in enumerate(taxonomy_relations):
            label = f"taxonomy_relations[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(
                row,
                {"from_node", "to_node", "relation_type", "strength"},
                label,
                errors,
            )
            from_node = row.get("from_node")
            to_node = row.get("to_node")
            rtype = row.get("relation_type")
            strength = row.get("strength")

            if rtype not in RELATION_TYPES:
                errors.append(f"{label}.relation_type: invalid value: {rtype}")
            if not isinstance(strength, (int, float)) or not (0 <= float(strength) <= 1):
                errors.append(f"{label}.strength: must be number in [0,1]")
            if not isinstance(from_node, str) or not from_node:
                errors.append(f"{label}.from_node: must be non-empty string")
            elif node_ids and from_node not in node_ids:
                errors.append(f"{label}.from_node: unknown node `{from_node}`")
            if not isinstance(to_node, str) or not to_node:
                errors.append(f"{label}.to_node: must be non-empty string")
            elif node_ids and to_node not in node_ids:
                errors.append(f"{label}.to_node: unknown node `{to_node}`")

            key = (str(from_node), str(to_node), str(rtype))
            if key in seen_rel:
                errors.append(f"{label}: duplicate relation {key}")
            seen_rel.add(key)

    official_refs = data.get("official_workflow_refs")
    if not isinstance(official_refs, list):
        errors.append("official_workflow_refs: must be an array")
    else:
        seen_caps_active: set[str] = set()
        for i, row in enumerate(official_refs):
            label = f"official_workflow_refs[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(
                row,
                {"source_url", "capability", "local_enforcement", "status"},
                label,
                errors,
            )
            cap = row.get("capability")
            if not isinstance(cap, str) or not cap.strip():
                errors.append(f"{label}.capability: must be a non-empty string")
            if row.get("status") not in WORKFLOW_STATUSES:
                errors.append(f"{label}.status: invalid value: {row.get('status')}")
            if str(row.get("status", "")).lower() == "active" and isinstance(cap, str):
                seen_caps_active.add(cap)
            if not str(row.get("source_url", "")).strip():
                errors.append(f"{label}.source_url: must be non-empty")
            if not str(row.get("local_enforcement", "")).strip():
                errors.append(f"{label}.local_enforcement: must be non-empty")

        missing_caps = sorted(OFFICIAL_CAPABILITIES_REQUIRED - seen_caps_active)
        if missing_caps:
            errors.append(
                "official_workflow_refs: missing active capabilities: " + ", ".join(missing_caps)
            )

    canonical_specs = data.get("canonical_specs")
    if not isinstance(canonical_specs, list):
        errors.append("canonical_specs: must be an array")
    else:
        seen_spec_ids: set[str] = set()
        for i, row in enumerate(canonical_specs):
            label = f"canonical_specs[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(
                row,
                {
                    "spec_id",
                    "repo",
                    "entry_file",
                    "entry_decl",
                    "required_decl_refs",
                    "forbidden_tokens",
                    "axiom_policy",
                    "closure_policy",
                    "status",
                },
                label,
                errors,
            )
            sid = row.get("spec_id")
            if not isinstance(sid, str) or not sid.strip():
                errors.append(f"{label}.spec_id: must be a non-empty string")
            elif sid in seen_spec_ids:
                errors.append(f"{label}.spec_id: duplicate spec_id `{sid}`")
            else:
                seen_spec_ids.add(sid)

            if row.get("status") not in CANONICAL_SPEC_STATUSES:
                errors.append(f"{label}.status: invalid value: {row.get('status')}")
            if row.get("axiom_policy") not in AXIOM_POLICIES:
                errors.append(f"{label}.axiom_policy: invalid value: {row.get('axiom_policy')}")
            if not isinstance(row.get("required_decl_refs"), list):
                errors.append(f"{label}.required_decl_refs: must be an array")
            if not isinstance(row.get("forbidden_tokens"), list):
                errors.append(f"{label}.forbidden_tokens: must be an array")
            for field in ("repo", "entry_file", "entry_decl", "closure_policy"):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    errors.append(f"{label}.{field}: must be a non-empty string")
            if row.get("repo") != "MLTheory":
                errors.append(f"{label}.repo: must be `MLTheory` in MLTheory SSOT")

    modules = data.get("modules")
    module_paths: set[str] = set()
    if not isinstance(modules, list):
        errors.append("modules: must be an array")
    else:
        expected_keys = {
            "module_path",
            "primary_node_id",
            "source_track",
            "status",
            "source",
            "book_refs",
            "layer",
            "proof_status",
            "placeholder_policy_scope",
            "role",
            "user_surface",
            "formal_decl_refs",
        }
        for i, row in enumerate(modules):
            label = f"modules[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(row, expected_keys, label, errors)

            module_path = row.get("module_path")
            if not isinstance(module_path, str) or not module_path:
                errors.append(f"{label}.module_path: must be a non-empty string")
            else:
                if module_path in module_paths:
                    errors.append(f"{label}.module_path: duplicate module_path: {module_path}")
                module_paths.add(module_path)
                if not _module_file_path(module_path).exists():
                    errors.append(f"{label}.module_path: missing local file for {module_path}")

            primary_node_id = row.get("primary_node_id")
            if not isinstance(primary_node_id, str) or not primary_node_id.strip():
                errors.append(f"{label}.primary_node_id: must be non-empty string")
            elif node_ids and primary_node_id not in node_ids:
                errors.append(f"{label}.primary_node_id: unknown node `{primary_node_id}`")

            source_track = row.get("source_track")
            if source_track not in SOURCE_TRACKS:
                errors.append(f"{label}.source_track: invalid value: {source_track}")

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
            scope = row.get("placeholder_policy_scope")
            if scope not in PLACEHOLDER_SCOPES:
                errors.append(f"{label}.placeholder_policy_scope: invalid value: {scope}")

            if layer in {"core", "methods"} and scope != "forbidden":
                errors.append(
                    f"{label}: core/methods modules must set placeholder_policy_scope=forbidden"
                )
            if scope == "forbidden" and proof_status == "placeholder":
                errors.append(
                    f"{label}: placeholder_policy_scope=forbidden but proof_status=placeholder"
                )

            role = row.get("role")
            if role not in MODULE_ROLES:
                errors.append(f"{label}.role: invalid value: {role}")
            if row.get("user_surface") not in USER_SURFACES:
                errors.append(f"{label}.user_surface: invalid value: {row.get('user_surface')}")

            formal_refs = row.get("formal_decl_refs")
            if not isinstance(formal_refs, list):
                errors.append(f"{label}.formal_decl_refs: must be an array")
            elif not all(isinstance(x, str) for x in formal_refs):
                errors.append(f"{label}.formal_decl_refs: all entries must be strings")

            if role in {"canonical", "tool"} and len(formal_refs) == 0 and module_path not in {
                "MLTheory.Core",
                "MLTheory.Methods",
                "MLTheory.Applications",
            }:
                warnings.append(
                    f"{label}: role={role} has empty formal_decl_refs (consider adding surfaced declarations)"
                )

            for pat in LEGACY_DOMAIN_BANNED_PATTERNS:
                if pat.search(module_path):
                    errors.append(f"{label}: legacy mixed-domain token in module_path: {module_path}")

    planned_modules = data.get("planned_modules")
    planned_paths: set[str] = set()
    if not isinstance(planned_modules, list):
        errors.append("planned_modules: must be an array")
    else:
        expected_keys = {"module_path", "target_node_id", "source_track", "status", "reason"}
        for i, row in enumerate(planned_modules):
            label = f"planned_modules[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(row, expected_keys, label, errors)

            module_path = row.get("module_path")
            if not isinstance(module_path, str) or not module_path:
                errors.append(f"{label}.module_path: must be non-empty string")
            else:
                if module_path in planned_paths:
                    errors.append(f"{label}.module_path: duplicate planned module_path: {module_path}")
                planned_paths.add(module_path)
                if module_path in module_paths:
                    errors.append(f"{label}.module_path: duplicated in modules and planned_modules: {module_path}")
                if _module_file_path(module_path).exists():
                    warnings.append(
                        f"{label}.module_path: file exists locally; consider moving to modules: {module_path}"
                    )

            target_node = row.get("target_node_id")
            if not isinstance(target_node, str) or not target_node.strip():
                errors.append(f"{label}.target_node_id: must be non-empty string")
            elif node_ids and target_node not in node_ids:
                errors.append(f"{label}.target_node_id: unknown node `{target_node}`")

            if row.get("source_track") not in PLANNED_SOURCE_TRACKS:
                errors.append(f"{label}.source_track: invalid value: {row.get('source_track')}")
            status = row.get("status")
            if status not in MODULE_STATUSES:
                errors.append(f"{label}.status: invalid value: {status}")
            reason = row.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{label}.reason: must be non-empty string")
                reason = ""

            if status == "partial" and reason and not _planned_partial_reason_has_evidence(reason):
                errors.append(
                    f"{label}: planned_modules.status=partial must include traceable evidence in reason "
                    "(e.g. source_url/candidate_repo/external/evidence)"
                )

    execution_backlog = data.get("execution_backlog")
    if not isinstance(execution_backlog, list):
        errors.append("execution_backlog: must be an array")
    else:
        expected_keys = {"module_path", "horizon", "priority", "why_now", "done_when"}
        seen_backlog_paths: set[str] = set()
        horizon_counts: dict[str, int] = defaultdict(int)
        for i, row in enumerate(execution_backlog):
            label = f"execution_backlog[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(row, expected_keys, label, errors)

            module_path = row.get("module_path")
            if not isinstance(module_path, str) or not module_path.strip():
                errors.append(f"{label}.module_path: must be non-empty string")
            else:
                if module_path in seen_backlog_paths:
                    errors.append(
                        f"{label}.module_path: duplicate execution backlog module_path: {module_path}"
                    )
                seen_backlog_paths.add(module_path)
                if module_path not in planned_paths:
                    errors.append(
                        f"{label}.module_path: must reference planned_modules entry: {module_path}"
                    )

            horizon = row.get("horizon")
            if horizon not in EXECUTION_HORIZONS:
                errors.append(f"{label}.horizon: invalid value: {horizon}")
            else:
                horizon_counts[horizon] += 1

            priority = row.get("priority")
            if priority not in EXECUTION_PRIORITIES:
                errors.append(f"{label}.priority: invalid value: {priority}")

            if not isinstance(row.get("why_now"), str) or not row.get("why_now", "").strip():
                errors.append(f"{label}.why_now: must be non-empty string")
            if not isinstance(row.get("done_when"), str) or not row.get("done_when", "").strip():
                errors.append(f"{label}.done_when: must be non-empty string")

        if len(execution_backlog) > 20:
            errors.append(
                "execution_backlog: should stay concise (<=20 items) to remain a practical short queue"
            )
        if len(execution_backlog) == 0:
            warnings.append("execution_backlog is empty; consider defining a short actionable queue")
        elif horizon_counts["near"] == 0:
            errors.append("execution_backlog: at least one `near` item is required")

    structure_cleanup_candidates = data.get("structure_cleanup_candidates")
    if not isinstance(structure_cleanup_candidates, list):
        errors.append("structure_cleanup_candidates: must be an array")
    else:
        expected_keys = {
            "module_path",
            "definition_file",
            "imported_by",
            "role",
            "execution_state",
            "priority",
            "batch",
            "compatibility_window",
            "remove_after_releases",
            "migration_started_epoch",
            "replacement_imports",
            "risk",
            "suggested_action",
        }
        seen_cleanup_paths: set[str] = set()
        for i, row in enumerate(structure_cleanup_candidates):
            label = f"structure_cleanup_candidates[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{label}: must be an object")
                continue
            _check_keys_exact(row, expected_keys, label, errors)

            module_path = row.get("module_path")
            if not isinstance(module_path, str) or not module_path.strip():
                errors.append(f"{label}.module_path: must be non-empty string")
            else:
                if module_path in seen_cleanup_paths:
                    errors.append(
                        f"{label}.module_path: duplicate cleanup candidate `{module_path}`"
                    )
                seen_cleanup_paths.add(module_path)
                if module_path not in module_paths:
                    errors.append(
                        f"{label}.module_path: must reference an existing modules entry: {module_path}"
                    )

            definition_file = row.get("definition_file")
            if not isinstance(definition_file, str) or not definition_file.strip():
                errors.append(f"{label}.definition_file: must be non-empty string")
            else:
                def_path = ROOT / definition_file
                if not def_path.exists():
                    errors.append(f"{label}.definition_file: missing file `{definition_file}`")

            imported_by = row.get("imported_by")
            if not isinstance(imported_by, list) or not imported_by:
                errors.append(f"{label}.imported_by: must be a non-empty string array")
            elif not all(isinstance(x, str) and x.strip() for x in imported_by):
                errors.append(f"{label}.imported_by: all entries must be non-empty strings")

            role = row.get("role")
            if role not in MODULE_ROLES:
                errors.append(f"{label}.role: invalid value: {role}")

            execution_state = row.get("execution_state")
            if execution_state not in CLEANUP_EXECUTION_STATES:
                errors.append(f"{label}.execution_state: invalid value: {execution_state}")

            priority = row.get("priority")
            if priority not in CLEANUP_PRIORITIES:
                errors.append(f"{label}.priority: invalid value: {priority}")

            batch = row.get("batch")
            if not isinstance(batch, str) or CLEANUP_BATCH_RE.match(batch) is None:
                errors.append(f"{label}.batch: invalid value: {batch}")

            compatibility_window = row.get("compatibility_window")
            if not isinstance(compatibility_window, str) or not compatibility_window.strip():
                errors.append(f"{label}.compatibility_window: must be non-empty string")
            else:
                m = COMPAT_RELEASE_WINDOW_RE.match(compatibility_window.strip())
                if m is None:
                    errors.append(
                        f"{label}.compatibility_window: expected `<N> release(s)`, got `{compatibility_window}`"
                    )
                else:
                    expected_remove_after = int(m.group(1))
                    if row.get("remove_after_releases") != expected_remove_after:
                        errors.append(
                            f"{label}.remove_after_releases must match compatibility_window ({expected_remove_after})"
                        )

            remove_after_releases = row.get("remove_after_releases")
            if not isinstance(remove_after_releases, int) or remove_after_releases < 1:
                errors.append(f"{label}.remove_after_releases: must be integer >= 1")

            migration_started_epoch = row.get("migration_started_epoch")
            if not isinstance(migration_started_epoch, int) or migration_started_epoch < 1:
                errors.append(f"{label}.migration_started_epoch: must be integer >= 1")
            elif cleanup_release_epoch is not None and migration_started_epoch > cleanup_release_epoch:
                errors.append(
                    f"{label}.migration_started_epoch ({migration_started_epoch}) cannot exceed meta.cleanup_release_epoch ({cleanup_release_epoch})"
                )

            replacement_imports = row.get("replacement_imports")
            if not isinstance(replacement_imports, list) or not replacement_imports:
                errors.append(f"{label}.replacement_imports: must be a non-empty string array")
            elif not all(isinstance(x, str) and x.strip() for x in replacement_imports):
                errors.append(f"{label}.replacement_imports: all entries must be non-empty strings")
            else:
                for rep in replacement_imports:
                    if rep not in module_paths:
                        warnings.append(
                            f"{label}.replacement_imports entry not found in modules: {rep}"
                        )

            if (
                isinstance(cleanup_release_epoch, int)
                and isinstance(remove_after_releases, int)
                and isinstance(migration_started_epoch, int)
            ):
                ready_now = cleanup_release_epoch >= (migration_started_epoch + remove_after_releases)
                if execution_state == "ready_to_remove" and not ready_now:
                    errors.append(
                        f"{label}: execution_state=ready_to_remove too early for current cleanup_release_epoch={cleanup_release_epoch}"
                    )
                if execution_state == "migrating" and ready_now:
                    errors.append(
                        f"{label}: execution_state=migrating but remove window already reached; set to ready_to_remove"
                    )

            if not isinstance(row.get("risk"), str) or not row.get("risk", "").strip():
                errors.append(f"{label}.risk: must be non-empty string")
            if not isinstance(row.get("suggested_action"), str) or not row.get(
                "suggested_action", ""
            ).strip():
                errors.append(f"{label}.suggested_action: must be non-empty string")

        if len(structure_cleanup_candidates) == 0 and policy_tags:
            stale_tags = sorted(
                {
                    tag
                    for tag in policy_tags
                    if any(pat.match(tag) for pat in CLEANUP_TRANSIENT_POLICY_PATTERNS)
                }
            )
            if stale_tags:
                errors.append(
                    "meta.policy contains stale cleanup transient tags while "
                    "structure_cleanup_candidates is empty: "
                    + ", ".join(stale_tags)
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
                        {"chapter", "Corresponding module", "Override status", "Evidence link", "Gap description", "Follow-up actions"},
                        clabel,
                        errors,
                    )
                    if c.get("Override status") not in COVERAGE_STATUSES:
                        errors.append(f"{clabel}.Override status: invalid value: {c.get('Override status')}")
                    for ref in _iter_module_refs(str(c.get("Corresponding module", ""))):
                        coverage_module_refs.add(ref)

        combined_paths = set(module_paths)
        combined_paths.update(planned_paths)
        missing_coverage = sorted(combined_paths - coverage_module_refs)
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
        f"{len(data['taxonomy_nodes'])} taxonomy nodes, "
        f"{len(data['taxonomy_relations'])} taxonomy relations, "
        f"{len(data['official_workflow_refs'])} official refs, "
        f"{len(data['canonical_specs'])} canonical specs, "
        f"{len(data['modules'])} modules, "
        f"{len(data['planned_modules'])} planned_modules, "
        f"{len(data['execution_backlog'])} execution_backlog, "
        f"{len(data['structure_cleanup_candidates'])} cleanup_candidates, "
        f"{len(data['gaps'])} gaps, "
        f"{len(data['books'])} books, "
        f"{len(data['aliases'])} aliases."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
