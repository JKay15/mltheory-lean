#!/usr/bin/env python3
"""Migrate SSOT registry from flat-domain model to taxonomy v2.

This tool is intentionally idempotent on an already-migrated v2 registry:
- existing planned_modules are preserved and normalized;
- existing execution_backlog is preserved and normalized;
- planned source_track is hardened to {native, books};
- planned legacy paths are canonicalized to layered prefixes.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "ssot" / "registry.json"

PLANNED_PREFIX_BY_TARGET_NODE = {
    "probability": "MLTheory.Core.Probability",
    "statistics": "MLTheory.Core.Statistics",
    "learning": "MLTheory.Methods.Learning",
    "or": "MLTheory.Methods.OR",
    "oco": "MLTheory.Methods.OCO",
    "bandits": "MLTheory.Methods.Bandits",
    "rl": "MLTheory.Methods.RL",
    "ai": "MLTheory.Applications.AI",
    "llm": "MLTheory.Applications.LLM",
}

LEGACY_ROOTS_BY_TARGET_NODE = {
    "probability": ["MLTheory.Probability", "MLTheory.HDP"],
    "statistics": ["MLTheory.Statistics", "MLTheory.InfoTheory"],
    "learning": ["MLTheory.Learning", "MLTheory.Concentration"],
    "or": ["MLTheory.OR", "MLTheory.Optimization"],
    "oco": ["MLTheory.OCO"],
    "bandits": ["MLTheory.Bandits"],
    "rl": ["MLTheory.RL"],
    "ai": ["MLTheory.AI"],
    "llm": ["MLTheory.LLM"],
}
BACKLOG_HORIZONS = {"near", "mid", "far"}
BACKLOG_PRIORITIES = {"P1", "P2", "P3"}


def module_file_path(module_path: str) -> Path:
    if module_path == "MLTheory":
        return ROOT / "MLTheory.lean"
    return ROOT / f"{module_path.replace('.', '/')}.lean"


def taxonomy_nodes() -> list[dict]:
    return [
        {
            "node_id": "ml_root",
            "name": "MLTheory Root",
            "tier": "support",
            "primary_parent_id": None,
            "status": "active",
            "order": 0,
        },
        {
            "node_id": "foundations",
            "name": "Foundations",
            "tier": "foundation",
            "primary_parent_id": "ml_root",
            "status": "active",
            "order": 10,
        },
        {
            "node_id": "methods_problems",
            "name": "Methods and Problems",
            "tier": "methods",
            "primary_parent_id": "ml_root",
            "status": "active",
            "order": 20,
        },
        {
            "node_id": "applications_systems",
            "name": "Applications and Systems",
            "tier": "application",
            "primary_parent_id": "ml_root",
            "status": "active",
            "order": 30,
        },
        {
            "node_id": "support_infrastructure",
            "name": "Support Infrastructure",
            "tier": "support",
            "primary_parent_id": "ml_root",
            "status": "active",
            "order": 40,
        },
        {
            "node_id": "probability",
            "name": "Probability",
            "tier": "foundation",
            "primary_parent_id": "foundations",
            "status": "active",
            "order": 100,
        },
        {
            "node_id": "statistics",
            "name": "Statistics",
            "tier": "foundation",
            "primary_parent_id": "foundations",
            "status": "active",
            "order": 110,
        },
        {
            "node_id": "learning",
            "name": "Learning",
            "tier": "methods",
            "primary_parent_id": "methods_problems",
            "status": "active",
            "order": 200,
        },
        {
            "node_id": "or",
            "name": "OR",
            "tier": "methods",
            "primary_parent_id": "methods_problems",
            "status": "active",
            "order": 210,
        },
        {
            "node_id": "rl",
            "name": "RL",
            "tier": "methods",
            "primary_parent_id": "learning",
            "status": "active",
            "order": 220,
        },
        {
            "node_id": "ai",
            "name": "AI",
            "tier": "application",
            "primary_parent_id": "learning",
            "status": "active",
            "order": 300,
        },
        {
            "node_id": "llm",
            "name": "LLM",
            "tier": "application",
            "primary_parent_id": "ai",
            "status": "active",
            "order": 310,
        },
        {
            "node_id": "oco",
            "name": "OCO",
            "tier": "methods",
            "primary_parent_id": "or",
            "status": "active",
            "order": 230,
        },
        {
            "node_id": "bandits",
            "name": "Bandits",
            "tier": "methods",
            "primary_parent_id": "or",
            "status": "active",
            "order": 240,
        },
        {
            "node_id": "architecture",
            "name": "Architecture",
            "tier": "support",
            "primary_parent_id": "support_infrastructure",
            "status": "active",
            "order": 400,
        },
    ]


def taxonomy_relations() -> list[dict]:
    return [
        {
            "from_node": "statistics",
            "to_node": "probability",
            "relation_type": "related",
            "strength": 0.8,
        },
        {
            "from_node": "rl",
            "to_node": "ai",
            "relation_type": "related",
            "strength": 0.6,
        },
        {
            "from_node": "bandits",
            "to_node": "rl",
            "relation_type": "related",
            "strength": 0.8,
        },
    ]


def infer_primary_node(module_path: str, legacy_domain: str, layer: str) -> str:
    if module_path in {"MLTheory", "MLTheory.Core", "MLTheory.Methods", "MLTheory.Applications"}:
        return "architecture"
    if module_path.startswith("MLTheory.Core.Learning") or module_path.startswith(
        "MLTheory.Methods.Learning"
    ):
        return "learning"
    if module_path.startswith("MLTheory.Core.RL") or module_path.startswith(
        "MLTheory.Methods.RL"
    ):
        return "rl"
    if module_path.startswith("MLTheory.Applications.Learning"):
        return "learning"
    if module_path.startswith("MLTheory.Applications.RL"):
        return "rl"

    if module_path.startswith("MLTheory.Books.Durrett5"):
        return "probability"
    if module_path.startswith("MLTheory.Books.FoML2"):
        return "learning"
    if module_path.startswith("MLTheory.Books.SuttonBartoRL2"):
        return "rl"
    if module_path.startswith("MLTheory.Books.BanditAlgorithms"):
        return "bandits"
    if module_path.startswith("MLTheory.Books.HazanOCO2"):
        return "oco"
    if module_path == "MLTheory.Books":
        return "architecture"

    if module_path.startswith("MLTheory.Probability") or module_path.startswith("MLTheory.HDP"):
        return "probability"
    if module_path.startswith("MLTheory.Statistics") or module_path.startswith("MLTheory.InfoTheory"):
        return "statistics"
    if module_path.startswith("MLTheory.OR") or module_path.startswith("MLTheory.Optimization"):
        return "or"
    if module_path.startswith("MLTheory.OCO"):
        return "oco"
    if module_path.startswith("MLTheory.Bandits"):
        return "bandits"
    if module_path.startswith("MLTheory.RL"):
        return "rl"
    if module_path.startswith("MLTheory.Learning") or module_path.startswith("MLTheory.Concentration"):
        return "learning"
    if module_path.startswith("MLTheory.AI"):
        return "ai"
    if module_path.startswith("MLTheory.LLM"):
        return "llm"

    domain_map = {
        "Probability": "probability",
        "Statistics": "statistics",
        "Learning": "learning",
        "ML Theory": "learning",
        "OR": "or",
        "Operations Research": "or",
        "RL": "rl",
        "AI": "ai",
        "AI Theory": "ai",
        "LLM": "llm",
        "LLM Theory": "llm",
        "OCO": "oco",
        "Bandits": "bandits",
        "Architecture": "architecture",
        "Applications": "architecture",
        "Root": "architecture",
        "Durrett Index": "probability",
        "HDP Index": "probability",
        "Bandit Index": "bandits",
        "FoML2 Index": "learning",
        "RL2 Index": "rl",
        "OCO Index": "oco",
        "Book Index": "architecture",
    }
    if legacy_domain in domain_map:
        return domain_map[legacy_domain]

    if layer in {"core", "methods", "applications"}:
        return "architecture"
    return "learning"


def infer_source_track(module_path: str, legacy_domain: str, layer: str) -> str:
    if module_path.startswith("MLTheory.Books"):
        return "books"
    if legacy_domain.endswith("Index") or legacy_domain.endswith(" Index"):
        return "books"
    if legacy_domain == "Book Index":
        return "books"
    if module_path.startswith("MLTheory.HDP"):
        return "books"
    if layer == "legacy":
        return "legacy"
    return "native"


def _replace_prefix(module_path: str, old_prefix: str, new_prefix: str) -> str | None:
    if module_path == old_prefix:
        return new_prefix
    marker = old_prefix + "."
    if module_path.startswith(marker):
        return new_prefix + module_path[len(old_prefix) :]
    return None


def canonicalize_planned_module_path(
    module_path: str, target_node_id: str, source_track: str
) -> str:
    if source_track == "books":
        migrated = _replace_prefix(module_path, "MLTheory.HDP", "MLTheory.Books.VershyninHDP")
        if migrated:
            return migrated
        return module_path

    expected_prefix = PLANNED_PREFIX_BY_TARGET_NODE.get(target_node_id)
    if not expected_prefix:
        return module_path
    if module_path == expected_prefix or module_path.startswith(expected_prefix + "."):
        return module_path

    for legacy_root in LEGACY_ROOTS_BY_TARGET_NODE.get(target_node_id, []):
        migrated = _replace_prefix(module_path, legacy_root, expected_prefix)
        if migrated:
            return migrated

    return module_path


def normalize_planned_source_track(source_track: str) -> str:
    return "books" if source_track == "books" else "native"


def normalize_module_row(row: dict) -> dict:
    module_path = str(row.get("module_path", "")).strip()
    legacy_domain = str(row.get("domain", "")).strip()
    layer = str(row.get("layer", "")).strip()
    primary_node_id = (
        str(row.get("primary_node_id", "")).strip()
        or infer_primary_node(module_path, legacy_domain, layer)
    )
    source_track = (
        str(row.get("source_track", "")).strip()
        or infer_source_track(module_path, legacy_domain, layer)
    )

    return {
        "module_path": module_path,
        "primary_node_id": primary_node_id,
        "source_track": source_track,
        "status": str(row.get("status", "planned")),
        "source": str(row.get("source", "external")),
        "book_refs": str(row.get("book_refs", "")),
        "layer": layer,
        "proof_status": str(row.get("proof_status", "statement")),
        "placeholder_policy_scope": str(row.get("placeholder_policy_scope", "allowed")),
        "role": str(row.get("role", "placeholder")),
        "user_surface": str(row.get("user_surface", "internal")),
        "formal_decl_refs": list(row.get("formal_decl_refs", [])),
    }


def normalize_planned_row(row: dict) -> dict:
    module_path = str(row.get("module_path", "")).strip()
    target_node_id = str(row.get("target_node_id", "")).strip()
    source_track = normalize_planned_source_track(str(row.get("source_track", "")).strip())
    if not target_node_id:
        target_node_id = infer_primary_node(module_path, "", "")
    module_path = canonicalize_planned_module_path(module_path, target_node_id, source_track)
    status = str(row.get("status", "planned"))
    reason = str(row.get("reason", "")).strip() or "Planned module from legacy registry migration."
    return {
        "module_path": module_path,
        "target_node_id": target_node_id,
        "source_track": source_track,
        "status": status,
        "reason": reason,
    }


def normalize_execution_backlog(
    raw_backlog: object, planned_modules: list[dict]
) -> list[dict]:
    planned_paths = {row["module_path"] for row in planned_modules}
    if not isinstance(raw_backlog, list):
        return []

    normalized: list[dict] = []
    seen_paths: set[str] = set()
    for row in raw_backlog:
        if not isinstance(row, dict):
            continue
        module_path = str(row.get("module_path", "")).strip()
        if not module_path or module_path in seen_paths:
            continue
        if module_path not in planned_paths:
            continue

        horizon = str(row.get("horizon", "mid")).strip()
        if horizon not in BACKLOG_HORIZONS:
            horizon = "mid"
        priority = str(row.get("priority", "P2")).strip()
        if priority not in BACKLOG_PRIORITIES:
            priority = "P2"
        why_now = str(row.get("why_now", "")).strip() or "Planned focus item."
        done_when = str(row.get("done_when", "")).strip() or "Statement-level module completed."

        normalized.append(
            {
                "module_path": module_path,
                "horizon": horizon,
                "priority": priority,
                "why_now": why_now,
                "done_when": done_when,
            }
        )
        seen_paths.add(module_path)
    return normalized


def migrate(data: dict) -> dict:
    old_modules = data.get("modules", [])
    old_planned_modules = data.get("planned_modules", [])
    modules: list[dict] = []
    planned_modules: list[dict] = []

    for row in old_modules:
        normalized = normalize_module_row(row)
        module_path = normalized["module_path"]
        exists = module_file_path(module_path).exists()
        if exists:
            modules.append(normalized)
        else:
            planned_source_track = normalize_planned_source_track(normalized["source_track"])
            planned_path = canonicalize_planned_module_path(
                module_path, normalized["primary_node_id"], planned_source_track
            )
            planned_modules.append(
                {
                    "module_path": planned_path,
                    "target_node_id": normalized["primary_node_id"],
                    "source_track": planned_source_track,
                    "status": normalized["status"],
                    "reason": (
                        "No local .lean file yet; keep as roadmap/planned module "
                        f"(layer={normalized['layer']}, role={normalized['role']}, "
                        f"proof_status={normalized['proof_status']})."
                    ),
                }
            )

    if isinstance(old_planned_modules, list):
        for row in old_planned_modules:
            if not isinstance(row, dict):
                continue
            planned_modules.append(normalize_planned_row(row))

    module_paths_seen: set[str] = set()
    modules_dedup: list[dict] = []
    for row in modules:
        path = row["module_path"]
        if path in module_paths_seen:
            continue
        module_paths_seen.add(path)
        modules_dedup.append(row)
    modules = modules_dedup

    planned_paths_seen: set[str] = set()
    planned_dedup: list[dict] = []
    for row in planned_modules:
        path = row["module_path"]
        if path in module_paths_seen:
            continue
        if path in planned_paths_seen:
            continue
        planned_paths_seen.add(path)
        planned_dedup.append(row)
    planned_modules = planned_dedup
    execution_backlog = normalize_execution_backlog(
        data.get("execution_backlog", []), planned_modules
    )

    canonical_specs = [
        spec
        for spec in data.get("canonical_specs", [])
        if str(spec.get("repo", "")).strip() == "MLTheory"
    ]
    structure_cleanup_candidates = list(data.get("structure_cleanup_candidates", []))

    decisions = list(data.get("decisions", []))
    migration_decision = {
        "date": str(date.today()),
        "decision": (
            "Taxonomy v2 重整：采用层级树主导 + 三层标签；modules 仅保留真实 file-backed 模块，"
            "无文件条目迁移到 planned_modules；Books/Legacy 改为 source_track 轴。"
        ),
        "status": "active",
        "impact": (
            "结构可视化与治理从扁平 domain 迁移到 taxonomy_nodes/taxonomy_relations，"
            "减少语义混杂并提升独立验证可追踪性。"
        ),
    }
    if migration_decision["decision"] not in {d.get("decision") for d in decisions}:
        decisions.append(migration_decision)

    boundary_decision = {
        "date": str(date.today()),
        "decision": (
            "canonical_specs 三仓边界收敛：MLTheory SSOT 仅保留 repo=MLTheory 的通用 canonical 契约；"
            "paper-template 题目专属契约迁回论文仓脚本配置。"
        ),
        "status": "active",
        "impact": "避免跨仓 canonical 规则混放，降低边界漂移风险。",
    }
    if boundary_decision["decision"] not in {d.get("decision") for d in decisions}:
        decisions.append(boundary_decision)

    meta = dict(data.get("meta", {}))
    meta["schema_version"] = "1.4.0"
    meta["last_updated"] = str(date.today())
    policies = list(meta.get("policy", []))
    for p in (
        "taxonomy_v2_tree_first",
        "books_legacy_as_source_track",
        "modules_file_backed_only",
        "planned_modules_split",
        "execution_backlog_shortlist_enabled",
    ):
        if p not in policies:
            policies.append(p)
    meta["policy"] = policies

    return {
        "meta": meta,
        "decisions": decisions,
        "taxonomy_nodes": taxonomy_nodes(),
        "taxonomy_relations": taxonomy_relations(),
        "official_workflow_refs": list(data.get("official_workflow_refs", [])),
        "canonical_specs": canonical_specs,
        "modules": modules,
        "planned_modules": planned_modules,
        "execution_backlog": execution_backlog,
        "structure_cleanup_candidates": structure_cleanup_candidates,
        "gaps": list(data.get("gaps", [])),
        "books": list(data.get("books", [])),
        "aliases": list(data.get("aliases", [])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate registry.json to taxonomy v2 model.")
    parser.add_argument(
        "--registry",
        type=Path,
        default=REGISTRY_PATH,
        help="Path to registry.json (default: docs/ssot/registry.json)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write file; only report migration summary.",
    )
    args = parser.parse_args()

    src = json.loads(args.registry.read_text(encoding="utf-8"))
    dst = migrate(src)
    text = json.dumps(dst, ensure_ascii=False, indent=2) + "\n"

    if args.check:
        print(
            "[migrate_ssot_to_taxonomy_v2] "
            f"modules={len(dst['modules'])}, planned_modules={len(dst['planned_modules'])}, "
            f"canonical_specs={len(dst['canonical_specs'])}, taxonomy_nodes={len(dst['taxonomy_nodes'])}"
        )
        return 0

    args.registry.write_text(text, encoding="utf-8")
    print(
        "[migrate_ssot_to_taxonomy_v2] wrote "
        f"{args.registry} (modules={len(dst['modules'])}, planned_modules={len(dst['planned_modules'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
