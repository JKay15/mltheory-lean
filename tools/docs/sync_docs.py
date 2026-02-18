#!/usr/bin/env python3
"""Generate Markdown docs from docs/ssot/registry.json."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "ssot" / "registry.json"
LEAN4_AUDIT_PATH = ROOT / "docs" / "ssot" / "lean4_contract_audit.json"
META_TAXONOMY_PATH = ROOT / "docs" / "meta" / "taxonomy.yaml"
META_CANON_PATH = ROOT / "docs" / "meta" / "canon.yaml"
MODULES_INDEX_PATH = ROOT / "artifacts" / "index" / "modules.json"
GENERATED_NOTE = "<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->"
PARTIAL_REASON_EVIDENCE_TOKENS = (
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
PROMOTION_DECISION_RE = re.compile(
    r"`([^`]+)` Already from planned_modules elevated to reality file-backed module"
)
AUTO_BLOCK_RE = re.compile(
    r"(<!-- AUTO:(?P<name>[A-Z0-9_-]+) BEGIN -->)(?P<body>.*?)(<!-- AUTO:(?P=name) END -->)",
    re.DOTALL,
)


def load_registry() -> dict:
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing registry: {REGISTRY_PATH}")


def load_lean4_contract_audit() -> dict | None:
    try:
        return json.loads(LEAN4_AUDIT_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def esc(value: object) -> str:
    text = str(value)
    text = text.replace("|", "\\|")
    text = text.replace("\n", "<br>")
    return text


def table(headers: list[str], rows: list[list[object]]) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        out.append("| " + " | ".join(esc(x) for x in row) + " |")
    return "\n".join(out)


def _parse_simple_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    result: dict = {}
    section: str | None = None
    current: dict | None = None
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            stripped = line.strip()
            if indent == 0 and stripped.endswith(":"):
                if section in {"nodes", "bindings"} and current is not None:
                    result.setdefault(section, []).append(current)
                    current = None
                section = stripped[:-1]
                if section not in result:
                    result[section] = [] if section in {"nodes", "bindings"} else {}
                continue
            if section in {"nodes", "bindings"}:
                if stripped.startswith("- "):
                    if current is not None:
                        result[section].append(current)
                    current = {}
                    tail = stripped[2:].strip()
                    if ":" in tail:
                        k, v = tail.split(":", 1)
                        current[k.strip()] = v.strip().strip('"').strip("'")
                    continue
                if current is not None and ":" in stripped:
                    k, v = stripped.split(":", 1)
                    current[k.strip()] = v.strip().strip('"').strip("'")
                continue
            if section is not None and isinstance(result.get(section), dict):
                if ":" in stripped:
                    k, v = stripped.split(":", 1)
                    key = k.strip()
                    val = v.strip()
                    if val == "":
                        result[section][key] = []
                    else:
                        result[section][key] = val.strip('"').strip("'")
                elif stripped.startswith("- "):
                    keys = list(result[section].keys())
                    if keys:
                        result[section][keys[-1]].append(
                            stripped[2:].strip().strip('"').strip("'")
                        )
    if section in {"nodes", "bindings"} and current is not None:
        result.setdefault(section, []).append(current)
    return result


def _load_meta_index_source() -> dict | None:
    if not META_TAXONOMY_PATH.exists() or not MODULES_INDEX_PATH.exists():
        return None
    try:
        modules_payload = json.loads(MODULES_INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    modules = modules_payload.get("modules")
    if not isinstance(modules, list):
        return None
    taxonomy = _parse_simple_yaml(META_TAXONOMY_PATH)
    nodes = taxonomy.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return None
    canon = _parse_simple_yaml(META_CANON_PATH)
    canon_modules = {
        m for m in canon.get("canonical_modules", []) if isinstance(m, str) and m.strip()
    }
    binding_map: dict[str, str] = {}
    spine_modules: set[str] = set()
    for b in taxonomy.get("bindings", []):
        if not isinstance(b, dict):
            continue
        if b.get("kind") != "module":
            continue
        target = b.get("target")
        node = b.get("node")
        if isinstance(target, str) and isinstance(node, str):
            binding_map[target] = node
            if str(b.get("spine", "")).lower() == "true":
                spine_modules.add(target)
    return {
        "nodes": nodes,
        "modules": modules,
        "bindings": binding_map,
        "spine_modules": spine_modules,
        "canon_modules": canon_modules,
    }


def _toolforest_tier(node_id: str, parent: str | None) -> str:
    if parent is None:
        return "foundation"
    if node_id == "methods":
        return "methods"
    if node_id == "applications":
        return "application"
    return "support"


def _build_rows_from_meta_index(registry: dict, source: dict) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    taxonomy_nodes_raw = source["nodes"]
    modules_raw = source["modules"]
    binding_map = source["bindings"]
    spine_modules = source["spine_modules"]
    canon_modules = source["canon_modules"]

    taxonomy_nodes: list[dict] = []
    for idx, n in enumerate(taxonomy_nodes_raw):
        if not isinstance(n, dict):
            continue
        node_id = n.get("id")
        name = n.get("title")
        parent = n.get("parent")
        if not isinstance(node_id, str) or not isinstance(name, str):
            continue
        taxonomy_nodes.append(
            {
                "node_id": node_id,
                "name": name,
                "tier": _toolforest_tier(node_id, parent if isinstance(parent, str) else None),
                "primary_parent_id": parent if isinstance(parent, str) and parent else None,
                "status": "active",
                "order": idx,
            }
        )
    if not taxonomy_nodes:
        return [], [], [], []

    node_ids = {n["node_id"] for n in taxonomy_nodes}
    node_name = {n["node_id"]: n["name"] for n in taxonomy_nodes}
    root_node = next((n["node_id"] for n in taxonomy_nodes if n["primary_parent_id"] is None), taxonomy_nodes[0]["node_id"])

    def default_node_for_layer(layer: str) -> str:
        mapping = {
            "core": "core",
            "methods": "methods",
            "applications": "applications",
            "books": "books",
        }
        candidate = mapping.get(layer, root_node)
        return candidate if candidate in node_ids else root_node

    real_rows: list[dict] = []
    for m in sorted(modules_raw, key=lambda x: x.get("module", "")):
        if not isinstance(m, dict):
            continue
        module_path = m.get("module")
        layer = str(m.get("layer", "other"))
        if not isinstance(module_path, str):
            continue
        node_id = binding_map.get(module_path, default_node_for_layer(layer))
        if node_id not in node_ids:
            node_id = root_node
        subdomain, key_problem = _derive_subdomain_and_problem(module_path)
        role = "canonical" if module_path in canon_modules else "tool"
        proof_status = "proved" if module_path in spine_modules else "statement"
        real_rows.append(
            {
                "dataset": "real",
                "module_path": module_path,
                "node_id": node_id,
                "node_name": node_name.get(node_id, node_id),
                "source_track": "native",
                "status": "covered",
                "layer": layer,
                "role": role,
                "proof_status": proof_status,
                "formal_decl_refs": [],
                "subdomain": subdomain,
                "key_problem": key_problem,
                "reason": "",
                "execution_horizon": "",
                "execution_priority": "",
                "in_backlog": False,
            }
        )

    backlog_map = {
        row["module_path"]: row
        for row in registry.get("execution_backlog", [])
        if isinstance(row, dict) and "module_path" in row
    }
    planned_rows: list[dict] = []
    for m in sorted(registry["planned_modules"], key=lambda x: x["module_path"]):
        subdomain, key_problem = _derive_subdomain_and_problem(m["module_path"])
        backlog = backlog_map.get(m["module_path"], {})
        node_id = m["target_node_id"] if m["target_node_id"] in node_ids else root_node
        planned_rows.append(
            {
                "dataset": "planned",
                "module_path": m["module_path"],
                "node_id": node_id,
                "node_name": node_name.get(node_id, node_id),
                "source_track": m["source_track"],
                "status": m["status"],
                "layer": "planned",
                "role": "planned",
                "proof_status": "placeholder",
                "formal_decl_refs": [],
                "subdomain": subdomain,
                "key_problem": key_problem,
                "reason": m["reason"],
                "execution_horizon": backlog.get("horizon", "unscheduled"),
                "execution_priority": backlog.get("priority", ""),
                "in_backlog": bool(backlog),
            }
        )

    relations: list[dict] = []
    for n in taxonomy_nodes:
        pid = n["primary_parent_id"]
        if pid is None:
            continue
        relations.append(
            {
                "from_node": n["node_id"],
                "to_node": pid,
                "relation_type": "secondary_parent",
                "strength": 1.0,
            }
        )
    return taxonomy_nodes, relations, real_rows, planned_rows


def _tool_forest_source(registry: dict) -> tuple[list[dict], list[dict], list[dict], list[dict], str]:
    meta_source = _load_meta_index_source()
    if meta_source is not None:
        taxonomy_nodes, relations, real_rows, planned_rows = _build_rows_from_meta_index(registry, meta_source)
        if taxonomy_nodes and real_rows:
            return taxonomy_nodes, relations, real_rows, planned_rows, "meta_index"
    real_rows, planned_rows = _build_forest_rows(registry)
    return (
        _taxonomy_nodes_sorted(registry),
        registry["taxonomy_relations"],
        real_rows,
        planned_rows,
        "ssot",
    )


def _merge_auto_blocks(existing: str, generated: str) -> str:
    generated_blocks = {m.group("name"): m for m in AUTO_BLOCK_RE.finditer(generated)}
    if not generated_blocks:
        return generated
    existing_block_names = {m.group("name") for m in AUTO_BLOCK_RE.finditer(existing)}
    if not existing_block_names:
        return generated

    merged = existing
    for name, gm in generated_blocks.items():
        if name not in existing_block_names:
            return generated
        pattern = re.compile(
            rf"(<!-- AUTO:{name} BEGIN -->)(.*?)(<!-- AUTO:{name} END -->)",
            re.DOTALL,
        )
        replacement = gm.group(0)
        merged = pattern.sub(replacement, merged)
    return merged


def _doc_auto_block_name(path: Path) -> str:
    rel = path.relative_to(ROOT)
    token = "_".join(rel.parts)
    token = token.replace(".", "_")
    token = re.sub(r"[^A-Za-z0-9_]+", "_", token).strip("_").upper()
    return f"DOC-{token}"


def _wrap_generated_doc_with_auto_block(path: Path, content: str) -> str:
    # Preserve files that already define fine-grained AUTO blocks.
    if "<!-- AUTO:" in content:
        return content
    block = _doc_auto_block_name(path)
    body = content.rstrip("\n")
    return (
        f"<!-- AUTO:{block} BEGIN -->\n"
        f"{body}\n"
        f"<!-- AUTO:{block} END -->\n"
    )


def _has_partial_evidence_reason(reason: str) -> bool:
    lowered = reason.lower()
    if "no local .lean file yet" in lowered:
        return False
    return any(tok in lowered for tok in PARTIAL_REASON_EVIDENCE_TOKENS)


def render_decision_log(registry: dict) -> str:
    decisions = list(enumerate(registry["decisions"]))
    decisions.sort(key=lambda item: (item[1]["date"], item[0]))
    rows = [
        [row["date"], row["decision"], row["status"], row["impact"]]
        for _, row in decisions
    ]
    return "\n".join(
        [
            "# Decision log",
            "",
            GENERATED_NOTE,
            "",
            table(["date", "decision", "status", "impact"], rows),
            "",
        ]
    )


def render_module_catalog(registry: dict) -> str:
    node_name = {n["node_id"]: n["name"] for n in registry["taxonomy_nodes"]}
    modules = sorted(registry["modules"], key=lambda m: m["module_path"])
    planned_modules = sorted(registry["planned_modules"], key=lambda m: m["module_path"])
    backlog_map = {
        row["module_path"]: row
        for row in registry.get("execution_backlog", [])
        if isinstance(row, dict) and "module_path" in row
    }
    rows = []
    for m in modules:
        rows.append(
            [
                m["module_path"],
                m["primary_node_id"],
                node_name.get(m["primary_node_id"], m["primary_node_id"]),
                m["source_track"],
                m["status"],
                m["source"],
                m["book_refs"],
                m["layer"],
                m["proof_status"],
                m["placeholder_policy_scope"],
                m["role"],
                m["user_surface"],
                ", ".join(m["formal_decl_refs"]),
            ]
        )
    planned_rows = []
    for m in planned_modules:
        backlog = backlog_map.get(m["module_path"], {})
        planned_rows.append(
            [
                m["module_path"],
                m["target_node_id"],
                node_name.get(m["target_node_id"], m["target_node_id"]),
                m["source_track"],
                m["status"],
                backlog.get("horizon", "unscheduled"),
                backlog.get("priority", "-"),
                m["reason"],
            ]
        )
    return "\n".join(
        [
            "# Module summary(Module Catalog)",
            "",
            GENERATED_NOTE,
            "",
            "## real module(file-backed)Field constraints:",
            "- `module_path`",
            "- `primary_node_id`",
            "- `source_track(native/books/legacy)`",
            "- `status(planned/partial/covered/gap)`",
            "- `source(mathlib/slt/external)`",
            "- `book_refs`",
            "- `layer(core/methods/applications/books/legacy)`",
            "- `proof_status(placeholder/statement/proved)`",
            "- `placeholder_policy_scope(allowed/forbidden)`",
            "- `role(canonical/compat/bridge/tool/placeholder)`",
            "- `user_surface(public/internal)`",
            "- `formal_decl_refs`",
            "",
            table(
                [
                    "module_path",
                    "primary_node_id",
                    "primary_node_name",
                    "source_track(native/books/legacy)",
                    "status(planned/partial/covered/gap)",
                    "source(mathlib/slt/external)",
                    "book_refs",
                    "layer(core/methods/applications/books/legacy)",
                    "proof_status(placeholder/statement/proved)",
                    "placeholder_policy_scope(allowed/forbidden)",
                    "role(canonical/compat/bridge/tool/placeholder)",
                    "user_surface(public/internal)",
                    "formal_decl_refs",
                ],
                rows,
            ),
            "",
            "## planning module(non-file-backed)Field constraints:",
            "- `module_path`",
            "- `target_node_id`",
            "- `source_track(native/books)`",
            "- `status(planned/partial/covered/gap)`",
            "- `execution_horizon(near/mid/far/unscheduled)`:from `execution_backlog`(If not included in the short list, it is unscheduled)",
            "- `execution_priority(P1/P2/P3)`:from `execution_backlog`(If not included in the short list, it is `-`)",
            "- `status=partial` hour,`reason` Must contain traceability evidence(like external/source_url/candidate_repo/evidence)",
            "- `reason`",
            "",
            table(
                [
                    "module_path",
                    "target_node_id",
                    "target_node_name",
                    "source_track(native/books)",
                    "status(planned/partial/covered/gap)",
                    "execution_horizon",
                    "execution_priority",
                    "reason",
                ],
                planned_rows,
            ),
            "",
        ]
    )


def _detect_structure_issues(registry: dict) -> list[dict]:
    modules = list(registry["modules"])
    planned = list(registry["planned_modules"])
    aliases = list(registry["aliases"])
    node_name = _node_name_map(registry)

    real_count = Counter(m["primary_node_id"] for m in modules)
    planned_count = Counter(m["target_node_id"] for m in planned)

    issues: list[dict] = []

    # P1: Hollow nodes: many planned modules but zero real file-backed modules.
    hollow_hotspots = []
    for node_id, count in sorted(planned_count.items(), key=lambda x: (-x[1], x[0])):
        if real_count.get(node_id, 0) == 0 and count >= 10:
            hollow_hotspots.append((node_id, count))
    if hollow_hotspots:
        evidence = ";".join(
            f"{node_name.get(n, n)}: real=0 planned={c}" for n, c in hollow_hotspots
        )
        issues.append(
            {
                "issue_id": "S1",
                "severity": "P1",
                "title": "Main tree hollow node(A lot of planning,The real module is 0)",
                "evidence": evidence,
                "scope": f"{sum(c for _, c in hollow_hotspots)} planning module",
                "action": "First supplement each hotspot node 1 indivual file-backed skeleton entrance(Proof of non-placeholder),Press the book again/Topics are gradually populated.",
                "acceptance_gate": "Corresponding node real_modules >= 1;lake build + check_namespace_layout pass.",
                "rollback_point": "Only add skeleton files and import;If you are not satisfied, you can roll back the batch of new files and the corresponding import.",
            }
        )

    # P1: Public placeholder modules are confusing as user-facing API.
    public_placeholders = [
        m for m in modules if m["role"] == "placeholder" and m["user_surface"] == "public"
    ]
    if public_placeholders:
        names = ", ".join(m["module_path"] for m in public_placeholders)
        issues.append(
            {
                "issue_id": "S2",
                "severity": "P1",
                "title": "Public entrance remains placeholder",
                "evidence": f"{len(public_placeholders)} indivual:{names}",
                "scope": "applications User portal",
                "action": "Bundle placeholder The entrance is downgraded to internal,or change to bridge/compat and explicitly point to available canonical Entrance.",
                "acceptance_gate": "role=placeholder and user_surface=public The real number of modules is 0.",
                "rollback_point": "Change only registry Field(role/user_surface);Single rollback possible JSON change.",
            }
        )

    # P2: Active aliases still create dual-entry cognitive load.
    active_aliases = [a for a in aliases if a["status"] == "active"]
    if active_aliases:
        names = ", ".join(a["legacy_module"] for a in active_aliases[:6])
        if len(active_aliases) > 6:
            names += ", ..."
        issues.append(
            {
                "issue_id": "S3",
                "severity": "P2",
                "title": "There are still active alias,Coexistence of dual entrance tracks",
                "evidence": f"active aliases={len(active_aliases)};Example:{names}",
                "scope": "FoML2/SB2 Chapter compatible entrance",
                "action": "for each active alias Add decommissioning batches and windows,Switch to batch by batch deprecated and perform an anti-reflow scan.",
                "acceptance_gate": "active aliases Decrease monotonically by batch,and check_no_new_deprecated_imports keep passing.",
                "rollback_point": "If migration is blocked,will only be affected alias State switch back active,Not moving canonical document.",
            }
        )

    # P2: Statement debt in canonical/tool entry modules.
    statement_entries = [
        m
        for m in modules
        if m["role"] in {"canonical", "tool"} and m["proof_status"] == "statement"
    ]
    if statement_entries:
        names = ", ".join(m["module_path"] for m in statement_entries[:6])
        if len(statement_entries) > 6:
            names += ", ..."
        issues.append(
            {
                "issue_id": "S4",
                "severity": "P2",
                "title": "The key entry statement is already in,But the proof status is still statement",
                "evidence": f"{len(statement_entries)} modules;Example:{names}",
                "scope": "canonical/tool Credibility",
                "action": "according to canonical_specs Prioritize statement The entrance is advanced in batches to proved;First complement dependency closure shortest link.",
                "acceptance_gate": "canonical/tool of proved Ratio increases by batch,and canonical_contract keep passing.",
                "rollback_point": "When the proof of a single batch fails, only the batch will be rolled back. theorem change,Do not roll back passed batches.",
            }
        )

    # P3: planned partial modules must carry traceable external evidence.
    planned_status = Counter(m["status"] for m in planned)
    partial_planned = [m for m in planned if m["status"] == "partial"]
    partial_without_evidence = [
        m for m in partial_planned if not _has_partial_evidence_reason(m["reason"])
    ]
    if partial_without_evidence:
        names = ", ".join(m["module_path"] for m in partial_without_evidence[:6])
        if len(partial_without_evidence) > 6:
            names += ", ..."
        issues.append(
            {
                "issue_id": "S5",
                "severity": "P3",
                "title": "Planning module state semantics mixed(partial/gap exist simultaneously)",
                "evidence": (
                    f"planned status distributed:planned={planned_status.get('planned', 0)},"
                    f"partial={planned_status.get('partial', 0)},gap={planned_status.get('gap', 0)};"
                    f"no evidence partial={len(partial_without_evidence)}(Example:{names})"
                ),
                "scope": "Roadmap readability",
                "action": "convergence planned state semantics:Unimplemented files will be used first planned/gap,partial Only used if there is clear evidence of external reusability.",
                "acceptance_gate": "planned_modules of partial Entries have consistent justification templates and traceable sources.",
                "rollback_point": "Adjust only planned_modules.status/reason copywriting,Single rollback possible registry.",
            }
        )

    return issues


def render_structure_issues(registry: dict) -> str:
    issues = _detect_structure_issues(registry)
    active_issue_ids = {i["issue_id"] for i in issues}
    rows = [
        [
            i["issue_id"],
            i["severity"],
            i["title"],
            i["evidence"],
            i["scope"],
            i["action"],
            i["acceptance_gate"],
            i["rollback_point"],
        ]
        for i in issues
    ]

    phase_rows_raw = [
        [
            "Phase-1",
            "S1 + S2",
            "First make the hollow nodes public placeholder Convergence to available entry(Don't change theorem semantics)",
            "lake build + check_namespace_layout + check_placeholder_policy",
            "Roll back newly added skeleton files and registry Field changes",
        ],
        [
            "Phase-2",
            "S3",
            "active alias Decommissioning in batches,Ensure single-track user entrance",
            "check_no_new_deprecated_imports + ImportSmoke",
            "block alias from deprecated switch back active",
        ],
        [
            "Phase-3",
            "S4",
            "key canonical/tool from statement advance to proved",
            "check_canonical_contract + lake build",
            "Rollback only the current batch theorem,Does not affect converged batches",
        ],
        [
            "Phase-4",
            "S5",
            "tidy planned state semantics,Reduce roadmap ambiguity",
            "validate_ssot + sync_docs --check",
            "Rollback only planned_modules status and reason copywriting",
        ],
    ]
    phase_rows = []
    for phase, focus, goal, gates, rollback in phase_rows_raw:
        focus_ids = {x.strip() for x in focus.split("+")}
        status = "pending" if focus_ids & active_issue_ids else "done"
        phase_rows.append([phase, status, focus, goal, gates, rollback])

    return "\n".join(
        [
            "# Structural Issues Ledger(Structure Issues)",
            "",
            GENERATED_NOTE,
            "",
            "## What problem does this document solve?(human language)",
            "1. Not relying on subjective impression,directly from the current `registry.json` Statistical structure issues.",
            "2. Give evidence for every question,Scope of influence,Next action,Acceptance of access control,rollback point.",
            "3. The goal is to make 'what to fix first, how to fix it, and how to roll back' visible at a glance.",
            "",
            "## Current automatically identified issues",
            table(
                [
                    "issue_id",
                    "severity",
                    "title",
                    "evidence",
                    "scope",
                    "action",
                    "acceptance_gate",
                    "rollback_point",
                ],
                rows,
            ),
            "",
            "## batch reordering(Can be rolled back)",
            table(
                ["phase", "status", "focus_issues", "goal", "gates", "rollback"],
                phase_rows,
            ),
            "",
            "## Usage",
            "1. Look at the highest first severity question(if exists `P1`,Prioritize repair `P1`).",
            "2. Each batch is completed,All running correspondence gates;Those who fail to pass the gate will not be admitted to the next batch..",
            "3. If a batch is stuck,According to the batch rollback Withdraw first,Split into smaller batches and try again.",
            "",
        ]
    )


def render_execution_backlog(registry: dict) -> str:
    node_name = _node_name_map(registry)
    planned_by_path = {m["module_path"]: m for m in registry["planned_modules"]}
    backlog = list(registry.get("execution_backlog", []))

    horizon_order = ("near", "mid", "far")
    by_horizon: dict[str, list[dict]] = {h: [] for h in horizon_order}
    for row in backlog:
        if not isinstance(row, dict):
            continue
        h = row.get("horizon")
        if h in by_horizon:
            by_horizon[h].append(row)

    for h in horizon_order:
        by_horizon[h].sort(key=lambda x: (x.get("priority", "P9"), x.get("module_path", "")))

    backlog_paths = {
        row.get("module_path")
        for row in backlog
        if isinstance(row, dict) and isinstance(row.get("module_path"), str)
    }
    unscheduled = sorted(
        m["module_path"] for m in registry["planned_modules"] if m["module_path"] not in backlog_paths
    )

    lines = [
        "# Planning execution checklist(Execution Backlog)",
        "",
        GENERATED_NOTE,
        "",
        "## Understand at a glance",
        f"- Total number of planning modules:{len(registry['planned_modules'])}",
        f"- Total number of execution shortlists:{len(backlog)}",
        f"- Not scheduled(unscheduled):{len(unscheduled)}",
        "- explain:`near`=The last two rounds will be advanced,`mid`=Follow-up stage,`far`=long term exploration.",
        "",
        "## near(Recently)",
    ]

    near_rows = []
    for row in by_horizon["near"]:
        module_path = row["module_path"]
        target_node = planned_by_path.get(module_path, {}).get("target_node_id", "-")
        near_rows.append(
            [
                row["priority"],
                module_path,
                node_name.get(target_node, target_node),
                row["why_now"],
                row["done_when"],
            ]
        )
    lines.append(
        table(["priority", "module_path", "target_node", "why_now", "done_when"], near_rows)
    )
    lines.extend(["", "## mid(medium term)"])

    mid_rows = []
    for row in by_horizon["mid"]:
        module_path = row["module_path"]
        target_node = planned_by_path.get(module_path, {}).get("target_node_id", "-")
        mid_rows.append(
            [
                row["priority"],
                module_path,
                node_name.get(target_node, target_node),
                row["why_now"],
                row["done_when"],
            ]
        )
    lines.append(
        table(["priority", "module_path", "target_node", "why_now", "done_when"], mid_rows)
    )
    lines.extend(["", "## far(forward)"])

    far_rows = []
    for row in by_horizon["far"]:
        module_path = row["module_path"]
        target_node = planned_by_path.get(module_path, {}).get("target_node_id", "-")
        far_rows.append(
            [
                row["priority"],
                module_path,
                node_name.get(target_node, target_node),
                row["why_now"],
                row["done_when"],
            ]
        )
    lines.append(
        table(["priority", "module_path", "target_node", "why_now", "done_when"], far_rows)
    )

    unscheduled_rows = [[m] for m in unscheduled[:25]]
    lines.extend(
        [
            "",
            "## Unscheduled modules(Top 25)",
            table(["module_path"], unscheduled_rows),
            "",
            "## Usage",
            "1. Only from `near` Litori 1-2 Item advancement,Avoid quality degradation caused by excessive concurrency.",
            "2. only completed `done_when`,Items are allowed to be moved from short-list Move out or downgrade to `mid/far`.",
            "3. When adding a new planning module,Prioritize whether to enter `execution_backlog`,Otherwise default `unscheduled`.",
            "",
        ]
    )
    return "\n".join(lines)


def render_review_dashboard(registry: dict) -> str:
    node_name = _node_name_map(registry)
    modules = sorted(registry["modules"], key=lambda m: m["module_path"])
    planned_modules = sorted(registry["planned_modules"], key=lambda m: m["module_path"])
    backlog = list(registry.get("execution_backlog", []))
    module_map = {m["module_path"]: m for m in modules}

    recent_promotions = _extract_recent_promotions(registry, limit=10)
    recent_rows = []
    for module_path in recent_promotions:
        mod = module_map.get(module_path)
        if mod is None:
            recent_rows.append([module_path, "-", "-", "-", "-"])
            continue
        recent_rows.append(
            [
                module_path,
                node_name.get(mod["primary_node_id"], mod["primary_node_id"]),
                mod["role"],
                mod["proof_status"],
                _decl_preview(mod["formal_decl_refs"], limit=3),
            ]
        )

    horizon_rank = {"near": 0, "mid": 1, "far": 2}
    backlog_rows = []
    for row in sorted(
        [r for r in backlog if isinstance(r, dict)],
        key=lambda r: (
            horizon_rank.get(str(r.get("horizon", "")), 9),
            _priority_rank(str(r.get("priority", "P9"))),
            str(r.get("module_path", "")),
        ),
    ):
        mpath = str(row.get("module_path", ""))
        planned = next((x for x in planned_modules if x["module_path"] == mpath), None)
        target = planned["target_node_id"] if planned else "-"
        backlog_rows.append(
            [
                row.get("horizon", "-"),
                row.get("priority", "-"),
                mpath,
                node_name.get(target, target),
                row.get("why_now", "-"),
                row.get("done_when", "-"),
            ]
        )

    real_count = Counter(m["primary_node_id"] for m in modules)
    planned_count = Counter(m["target_node_id"] for m in planned_modules)
    node_rows = []
    for n in _taxonomy_nodes_sorted(registry):
        nid = n["node_id"]
        node_rows.append(
            [
                n["name"],
                nid,
                real_count.get(nid, 0),
                planned_count.get(nid, 0),
            ]
        )
    node_rows.sort(key=lambda x: (-x[3], x[2], x[0]))

    gate_commands = [
        "python3 tools/docs/validate_ssot.py",
        "python3 tools/docs/sync_docs.py --check",
        "python3 tools/ci/check_taxonomy_contract.py",
        "python3 tools/ci/check_tool_forest_consistency.py",
        "python3 tools/ci/check_review_views_consistency.py",
        "bash tools/ci/check_canonical_contract.sh",
        "bash tools/ci/check_official_workflow_alignment.sh",
        "bash tools/ci/check_no_sorry_axiom.sh",
        "~/.elan/bin/lake build",
    ]

    lines = [
        "# Acceptance Kanban(Review Dashboard)",
        "",
        GENERATED_NOTE,
        "",
        "## Look at these four things first",
        f"1. real module:`{len(modules)}`",
        f"2. planning module:`{len(planned_modules)}`",
        f"3. Current short list:`{len(backlog_rows)}`",
        f"4. Recently promoted(planned -> file-backed):`{len(recent_rows)}`",
        "",
        "## Recently promoted(planned -> file-backed)",
        table(
            ["module_path", "node", "role", "proof_status", "Read the statement first(Top3)"],
            recent_rows if recent_rows else [["(None yet)", "-", "-", "-", "-"]],
        ),
        "",
        "## Current execution focus(execution_backlog)",
        table(
            ["horizon", "priority", "module_path", "target_node", "why_now", "done_when"],
            backlog_rows if backlog_rows else [["-", "-", "(null)", "-", "-", "-"]],
        ),
        "",
        "## structural hot zone(Sort by planning pressure)",
        table(["node_name", "node_id", "real_modules", "planned_modules"], node_rows[:8]),
        "",
        "## One-click acceptance command",
        "pass standard:All the above commands `PASS` / `Build completed successfully`.",
        "```bash",
        *gate_commands,
        "```",
        "",
        "## How to use(human language)",
        "1. Check 'Recently promoted' first to confirm this batch matches the intended direction.",
        "2. Then check 'Current execution focus' to confirm the next-step priority.",
        "3. Finally run the 'One-click acceptance commands' to ensure independent reproducibility.",
        "",
    ]
    return "\n".join(lines)


def render_api_cards(registry: dict) -> str:
    node_name = _node_name_map(registry)
    modules = sorted(registry["modules"], key=lambda m: m["module_path"])
    public_modules = [m for m in modules if m["user_surface"] == "public"]
    if not public_modules:
        public_modules = modules

    recent_promotions = set(_extract_recent_promotions(registry, limit=12))
    by_node: dict[str, list[dict]] = defaultdict(list)
    for m in public_modules:
        by_node[m["primary_node_id"]].append(m)

    role_desc = {
        "canonical": "main entrance",
        "tool": "Tool interface",
        "bridge": "bridge interface",
        "compat": "Compatible entrance",
        "placeholder": "Placeholder entrance",
    }
    layer_desc = {
        "core": "base layer",
        "methods": "method layer",
        "applications": "Application layer",
        "books": "book layer",
        "legacy": "Compatibility layer",
    }

    lines = [
        "# smallest API card(APICards)",
        "",
        GENERATED_NOTE,
        "",
        "## How to use(2 minute)",
        "1. Start with 'See recent changes first' and verify these items match expectations.",
        "2. Then go to the corresponding field grouping,View by module card:do what + Which statements to look at first.",
        "3. No need to read the entire database at once;Only spot checks in each round 3-5 Just one module.",
        "",
        "## See recent changes first",
    ]

    recent_rows = []
    for module_path in _extract_recent_promotions(registry, limit=10):
        mod = next((m for m in modules if m["module_path"] == module_path), None)
        if mod is None:
            recent_rows.append([module_path, "-", "-", "-"])
            continue
        recent_rows.append(
            [
                module_path,
                node_name.get(mod["primary_node_id"], mod["primary_node_id"]),
                f"{mod['layer']}/{mod['role']}/{mod['proof_status']}",
                _decl_preview(mod["formal_decl_refs"], limit=3),
            ]
        )
    lines.append(
        table(
            ["module_path", "node", "state(layer/role/proof)", "Read the statement first(Top3)"],
            recent_rows if recent_rows else [["(None yet)", "-", "-", "-"]],
        )
    )
    lines.extend(["", "## View by area(public module)"])

    for nid in [n["node_id"] for n in _taxonomy_nodes_sorted(registry)]:
        mods = sorted(by_node.get(nid, []), key=lambda m: m["module_path"])
        if not mods:
            continue
        nname = node_name.get(nid, nid)
        lines.append("")
        lines.append(f"### {nname}({len(mods)})")
        for m in mods:
            mark = "[NEW] " if m["module_path"] in recent_promotions else ""
            purpose = (
                f"{layer_desc.get(m['layer'], m['layer'])}of"
                f"{role_desc.get(m['role'], m['role'])}"
            )
            lines.append(
                (
                    f"- {mark}`{m['module_path']}`:{purpose};"
                    f"Look first `{_decl_preview(m['formal_decl_refs'], limit=3)}`;"
                    f"state `{m['proof_status']}`;"
                    f"document `{_module_path_to_file(m['module_path'])}`"
                )
            )

    lines.extend(
        [
            "",
            "## Spot check suggestions",
            "1. Check first every time 1 indivual `NEW` module + 1 Old modules in the same field,Confirm whether the style is consistent.",
            "2. If the card description is inconsistent with the code,Prioritize repair SSOT,Regenerate the document.",
            "",
        ]
    )
    return "\n".join(lines)


def render_refactor_handoff(registry: dict) -> str:
    node_name = _node_name_map(registry)
    modules = sorted(registry["modules"], key=lambda m: m["module_path"])
    planned_modules = sorted(registry["planned_modules"], key=lambda m: m["module_path"])
    issues = _detect_structure_issues(registry)
    audit = load_lean4_contract_audit()

    horizon_rank = {"near": 0, "mid": 1, "far": 2}
    backlog_rows = []
    planned_by_path = {m["module_path"]: m for m in planned_modules}
    for row in sorted(
        [r for r in registry.get("execution_backlog", []) if isinstance(r, dict)],
        key=lambda r: (
            horizon_rank.get(str(r.get("horizon", "")), 9),
            _priority_rank(str(r.get("priority", "P9"))),
            str(r.get("module_path", "")),
        ),
    ):
        mpath = str(row.get("module_path", ""))
        target = planned_by_path.get(mpath, {}).get("target_node_id", "-")
        backlog_rows.append(
            [
                row.get("horizon", "-"),
                row.get("priority", "-"),
                mpath,
                node_name.get(target, target),
                row.get("why_now", "-"),
                row.get("done_when", "-"),
            ]
        )

    promotion_rows = []
    seen_promotion: set[str] = set()
    for decision_row in registry["decisions"]:
        decision_text = decision_row.get("decision", "")
        if not isinstance(decision_text, str):
            continue
        m = PROMOTION_DECISION_RE.search(decision_text)
        if not m:
            continue
        module_path = m.group(1)
        if module_path in seen_promotion:
            continue
        seen_promotion.add(module_path)
        mod = next((x for x in modules if x["module_path"] == module_path), None)
        if mod is None:
            promotion_rows.append(
                [decision_row.get("date", "-"), module_path, "-", "-", decision_row.get("impact", "-")]
            )
            continue
        promotion_rows.append(
            [
                decision_row.get("date", "-"),
                module_path,
                node_name.get(mod["primary_node_id"], mod["primary_node_id"]),
                f"{mod['layer']}/{mod['role']}/{mod['proof_status']}",
                decision_row.get("impact", "-"),
            ]
        )

    module_rows = []
    for m in modules:
        module_rows.append(
            [
                m["module_path"],
                _module_path_to_file(m["module_path"]),
                node_name.get(m["primary_node_id"], m["primary_node_id"]),
                m["source_track"],
                m["layer"],
                m["role"],
                m["proof_status"],
                ", ".join(m["formal_decl_refs"]),
            ]
        )

    planned_rows = []
    for m in planned_modules:
        planned_rows.append(
            [
                m["module_path"],
                node_name.get(m["target_node_id"], m["target_node_id"]),
                m["source_track"],
                m["status"],
                m["reason"],
            ]
        )

    taxonomy_rows = []
    for n in _taxonomy_nodes_sorted(registry):
        taxonomy_rows.append(
            [
                n["node_id"],
                n["name"],
                n["tier"],
                n["primary_parent_id"] or "root",
                n["status"],
                n["order"],
            ]
        )

    relation_rows = [
        [
            r["from_node"],
            node_name.get(r["from_node"], r["from_node"]),
            r["to_node"],
            node_name.get(r["to_node"], r["to_node"]),
            r["relation_type"],
            r["strength"],
        ]
        for r in registry["taxonomy_relations"]
    ]

    workflow_rows = [
        [row["capability"], row["source_url"], row["status"], row["local_enforcement"]]
        for row in registry["official_workflow_refs"]
    ]
    canonical_rows = [
        [
            row["spec_id"],
            row["repo"],
            row["entry_file"],
            row["entry_decl"],
            row["axiom_policy"],
            row["status"],
            ", ".join(row["required_decl_refs"]),
        ]
        for row in registry["canonical_specs"]
    ]

    issue_rows = [
        [
            i["issue_id"],
            i["severity"],
            i["title"],
            i["evidence"],
            i["action"],
            i["acceptance_gate"],
        ]
        for i in issues
    ]

    audit_rows = []
    audit_summary = "(not found lean4_contract_audit.json)"
    if isinstance(audit, dict):
        audit_summary = (
            f"date={audit.get('date', '-')};mode={audit.get('mode', '-')};"
            f"score={audit.get('score', '-')};status={audit.get('status', '-')}"
        )
        checks = audit.get("checks", [])
        if isinstance(checks, list):
            for idx, row in enumerate(checks, start=1):
                if not isinstance(row, dict):
                    continue
                hits = row.get("hits", [])
                hit_count = len(hits) if isinstance(hits, list) else 0
                audit_rows.append(
                    [
                        idx,
                        row.get("check_id", "-"),
                        row.get("title", "-"),
                        "PASS" if row.get("passed") else "FAIL",
                        hit_count,
                    ]
                )

    lines = [
        "# GPT5.2pro Refactoring the handover package(MLTheory Full implementation snapshot)",
        "",
        GENERATED_NOTE,
        "",
        "## Purpose(Give reconstruction model)",
        "1. This document is a snapshot of completed work to avoid context loss during refactoring.",
        "2. All data comes from `docs/ssot/registry.json`(and review documents `docs/ssot/lean4_contract_audit.json`).",
        "3. You can feed this document directly to GPT5.2pro,Let it update the reconstruction plan based on the real status quo.",
        "",
        "## Understand the current status at a glance",
        f"- SSOT schema_version:`{registry['meta']['schema_version']}`",
        f"- last_updated:`{registry['meta']['last_updated']}`",
        f"- Total number of decisions:`{len(registry['decisions'])}`",
        f"- real module(file-backed)total:`{len(modules)}`",
        f"- planning module(non-file-backed)total:`{len(planned_modules)}`",
        f"- Execute short list(execution_backlog)number of items:`{len(backlog_rows)}`",
        f"- aliases total:`{len(registry['aliases'])}`",
        f"- gaps total:`{len(registry['gaps'])}`",
        "",
        "## Current next step(short list)",
        table(
            ["horizon", "priority", "module_path", "target_node", "why_now", "done_when"],
            backlog_rows if backlog_rows else [["-", "-", "(null)", "-", "-", "-"]],
        ),
        "",
        "## architectural contract(Unbreakable by default when refactoring)",
        "### 1) taxonomy main tree",
        table(
            ["node_id", "name", "tier", "primary_parent_id", "status", "order"],
            taxonomy_rows,
        ),
        "",
        "### 2) taxonomy relationship edge(secondary_parent/related)",
        table(
            ["from_node", "from_name", "to_node", "to_name", "relation_type", "strength"],
            relation_rows if relation_rows else [["-", "-", "-", "-", "-", "-"]],
        ),
        "",
        "### 3) Official workflow alignment(Lean Official resource mapping)",
        table(
            ["capability", "source_url", "status", "local_enforcement"],
            workflow_rows,
        ),
        "",
        "### 4) canonical spec contract",
        table(
            [
                "spec_id",
                "repo",
                "entry_file",
                "entry_decl",
                "axiom_policy",
                "status",
                "required_decl_refs",
            ],
            canonical_rows,
        ),
        "",
        "## Phase-0 / skill Alignment review snapshot",
        f"- {audit_summary}",
        table(
            ["#", "check_id", "title", "result", "hits"],
            audit_rows if audit_rows else [["-", "-", "-", "-", "-"]],
        ),
        "",
        "## Completed implementation(planned -> file-backed Ascension trajectory)",
        table(
            ["date", "module_path", "node", "state(layer/role/proof)", "impact"],
            promotion_rows if promotion_rows else [["-", "-", "-", "-", "-"]],
        ),
        "",
        "## Full list of real modules(Implementation details)",
        table(
            [
                "module_path",
                "file_path",
                "node",
                "source_track",
                "layer",
                "role",
                "proof_status",
                "formal_decl_refs",
            ],
            module_rows,
        ),
        "",
        "## Full list of planning modules(Not yet landed)",
        table(
            ["module_path", "target_node", "source_track", "status", "reason"],
            planned_rows,
        ),
        "",
        "## Structural Risks and Refactoring Priorities(automatic recognition)",
        table(
            ["issue_id", "severity", "title", "evidence", "action", "acceptance_gate"],
            issue_rows if issue_rows else [["-", "-", "(none)", "-", "-", "-"]],
        ),
        "",
        "## Reproducible acceptance command(After refactoring, run at least these)",
        "```bash",
        "python3 tools/docs/validate_ssot.py",
        "python3 tools/docs/sync_docs.py --check",
        "python3 tools/ci/check_taxonomy_contract.py",
        "python3 tools/ci/check_namespace_layout.py",
        "python3 tools/ci/check_tool_forest_consistency.py",
        "python3 tools/ci/check_review_views_consistency.py",
        "python3 tools/ci/check_registry_reference_hygiene.py",
        "python3 tools/ci/check_ready_to_remove.py",
        "bash tools/ci/check_ssot_migration_idempotent.sh",
        "bash tools/ci/check_layer_imports.sh",
        "bash tools/ci/check_no_new_deprecated_imports.sh",
        "bash tools/ci/check_canonical_contract.sh",
        "bash tools/ci/check_official_workflow_alignment.sh",
        "bash tools/ci/check_placeholder_policy.sh",
        "bash tools/ci/check_no_sorry_axiom.sh",
        "~/.elan/bin/lake build",
        "bash /Users/xiongjiangkai/xjk_papers/paper-template/scripts/formalization_preflight.sh --mode augmented",
        "bash /Users/xiongjiangkai/xjk_papers/paper-template/scripts/check_final_signature.sh",
        "```",
        "",
        "## Give GPT5.2pro Suggested reading order for",
        "1. Read 'architectural contract' and 'Phase-0 review snapshot' first to confirm hard constraints.",
        "2. Then read 'completed implementation trajectory' and the full real-module list to avoid duplication.",
        "3. Finally read 'planning modules + structural risk' to decide rewrite scope and migration strategy.",
        "",
    ]
    return "\n".join(lines)


def _mermaid_id(raw: str) -> str:
    safe = []
    for ch in raw:
        if ch.isalnum():
            safe.append(ch)
        else:
            safe.append("_")
    return "".join(safe)


def _derive_subdomain_and_problem(module_path: str) -> tuple[str, str]:
    parts = module_path.split(".")
    tail = parts[1:] if parts and parts[0] == "MLTheory" else parts
    if not tail:
        return ("Unknown", "(root)")

    head = tail[0]
    if head in {"Core", "Methods", "Applications"}:
        domain_tag = tail[1] if len(tail) > 1 else "General"
        subdomain = f"{head}.{domain_tag}"
        problem = ".".join(tail[2:]) if len(tail) > 2 else "(root)"
        return (subdomain, problem)
    if head == "Books":
        book_tag = tail[1] if len(tail) > 1 else "General"
        subdomain = f"Books.{book_tag}"
        problem = ".".join(tail[2:]) if len(tail) > 2 else "(root)"
        return (subdomain, problem)

    subdomain = head
    problem = ".".join(tail[1:]) if len(tail) > 1 else "(root)"
    return (subdomain, problem)


def _taxonomy_nodes_sorted(registry: dict) -> list[dict]:
    return sorted(registry["taxonomy_nodes"], key=lambda n: (n["order"], n["node_id"]))


def _node_name_map(registry: dict) -> dict[str, str]:
    return {n["node_id"]: n["name"] for n in registry["taxonomy_nodes"]}


def _module_path_to_file(module_path: str) -> str:
    if module_path == "MLTheory":
        return "MLTheory.lean"
    return module_path.replace(".", "/") + ".lean"


def _decl_preview(decls: list[str], limit: int = 3) -> str:
    if not decls:
        return "-"
    if len(decls) <= limit:
        return ", ".join(decls)
    shown = ", ".join(decls[:limit])
    return f"{shown}, ...(+{len(decls) - limit})"


def _extract_recent_promotions(registry: dict, limit: int = 8) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for row in reversed(registry["decisions"]):
        decision = row.get("decision", "")
        if not isinstance(decision, str):
            continue
        m = PROMOTION_DECISION_RE.search(decision)
        if not m:
            continue
        module_path = m.group(1)
        if module_path in seen:
            continue
        out.append(module_path)
        seen.add(module_path)
        if len(out) >= limit:
            break
    return out


def _priority_rank(priority: str) -> int:
    return {"P1": 1, "P2": 2, "P3": 3}.get(priority, 9)


def _short_text(text: str, limit: int = 88) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _build_forest_rows(registry: dict) -> tuple[list[dict], list[dict]]:
    node_name = _node_name_map(registry)
    backlog_map = {
        row["module_path"]: row
        for row in registry.get("execution_backlog", [])
        if isinstance(row, dict) and "module_path" in row
    }
    real_rows: list[dict] = []
    for m in sorted(registry["modules"], key=lambda x: x["module_path"]):
        subdomain, key_problem = _derive_subdomain_and_problem(m["module_path"])
        real_rows.append(
            {
                "dataset": "real",
                "module_path": m["module_path"],
                "node_id": m["primary_node_id"],
                "node_name": node_name.get(m["primary_node_id"], m["primary_node_id"]),
                "source_track": m["source_track"],
                "status": m["status"],
                "layer": m["layer"],
                "role": m["role"],
                "proof_status": m["proof_status"],
                "formal_decl_refs": list(m["formal_decl_refs"]),
                "subdomain": subdomain,
                "key_problem": key_problem,
                "reason": "",
                "execution_horizon": "",
                "execution_priority": "",
                "in_backlog": False,
            }
        )

    planned_rows: list[dict] = []
    for m in sorted(registry["planned_modules"], key=lambda x: x["module_path"]):
        subdomain, key_problem = _derive_subdomain_and_problem(m["module_path"])
        backlog = backlog_map.get(m["module_path"], {})
        in_backlog = bool(backlog)
        planned_rows.append(
            {
                "dataset": "planned",
                "module_path": m["module_path"],
                "node_id": m["target_node_id"],
                "node_name": node_name.get(m["target_node_id"], m["target_node_id"]),
                "source_track": m["source_track"],
                "status": m["status"],
                "layer": "planned",
                "role": "planned",
                "proof_status": "placeholder",
                "formal_decl_refs": [],
                "subdomain": subdomain,
                "key_problem": key_problem,
                "reason": m["reason"],
                "execution_horizon": backlog.get("horizon", "unscheduled"),
                "execution_priority": backlog.get("priority", ""),
                "in_backlog": in_backlog,
            }
        )
    return real_rows, planned_rows


def render_tool_forest(registry: dict) -> str:
    taxonomy_nodes, relations, real_rows, planned_rows, source_mode = _tool_forest_source(registry)
    node_name = {n["node_id"]: n["name"] for n in taxonomy_nodes}
    planned_by_path = {m["module_path"]: m for m in registry["planned_modules"]}
    backlog = list(registry.get("execution_backlog", []))

    real_count = Counter(r["node_id"] for r in real_rows)
    planned_count = Counter(r["node_id"] for r in planned_rows)
    role_count = Counter(r["role"] for r in real_rows)
    source_real = Counter(r["source_track"] for r in real_rows)
    source_planned = Counter(r["source_track"] for r in planned_rows)
    proof_count = Counter(r["proof_status"] for r in real_rows)
    backlog_count = len(backlog)
    unscheduled_count = sum(1 for r in planned_rows if r["execution_horizon"] == "unscheduled")

    children = defaultdict(list)
    for n in taxonomy_nodes:
        pid = n["primary_parent_id"]
        if pid is not None:
            children[pid].append(n)

    view_a = ["```mermaid", "graph TD", '  root["MLTheory Taxonomy"]']
    for n in taxonomy_nodes:
        nid = _mermaid_id(f"node_{n['node_id']}")
        label = (
            f"{n['name']}<br/>tier:{n['tier']}<br/>"
            f"real:{real_count[n['node_id']]} planned:{planned_count[n['node_id']]}"
        )
        view_a.append(f'  {nid}["{label}"]')
    for n in taxonomy_nodes:
        nid = _mermaid_id(f"node_{n['node_id']}")
        pid = n["primary_parent_id"]
        if pid is None:
            view_a.append(f"  root --> {nid}")
        else:
            view_a.append(f"  {_mermaid_id(f'node_{pid}')} --> {nid}")
    view_a.append("```")

    node_rows = []
    for n in taxonomy_nodes:
        nid = n["node_id"]
        canon = sum(1 for r in real_rows if r["node_id"] == nid and r["role"] == "canonical")
        tool = sum(1 for r in real_rows if r["node_id"] == nid and r["role"] == "tool")
        node_rows.append(
            [
                n["node_id"],
                n["name"],
                n["tier"],
                n["primary_parent_id"] or "root",
                real_count[nid],
                planned_count[nid],
                canon,
                tool,
            ]
        )
    node_rows.sort(key=lambda x: (-x[4], -x[5], x[0]))

    relation_rows = [
        [
            r["from_node"],
            node_name.get(r["from_node"], r["from_node"]),
            r["to_node"],
            node_name.get(r["to_node"], r["to_node"]),
            r["relation_type"],
            r["strength"],
        ]
        for r in relations
    ]

    source_rows = [
        [track, source_real[track], source_planned[track]]
        for track in ("native", "books", "legacy")
    ]

    entry_rows_all = [
        [
            r["module_path"],
            r["node_name"],
            r["source_track"],
            r["layer"],
            r["role"],
            r["proof_status"],
            _decl_preview(r["formal_decl_refs"], limit=3),
        ]
        for r in real_rows
        if r["role"] in {"canonical", "tool"}
    ]
    entry_rows = entry_rows_all[:20]

    planned_top_rows_all = [
        [
            r["module_path"],
            r["node_name"],
            r["source_track"],
            r["status"],
            r["execution_horizon"],
            r["execution_priority"] or "-",
            _short_text(r["reason"], limit=72),
        ]
        for r in planned_rows
    ]
    planned_top_rows = planned_top_rows_all[:12]

    backlog_rows = []
    horizon_rank = {"near": 0, "mid": 1, "far": 2}
    for row in sorted(
        backlog,
        key=lambda x: (
            horizon_rank.get(str(x.get("horizon", "")), 9),
            str(x.get("priority", "P9")),
            str(x.get("module_path", "")),
        ),
    ):
        module_path = str(row.get("module_path", ""))
        target_node = planned_by_path.get(module_path, {}).get("target_node_id", "-")
        backlog_rows.append(
            [
                row.get("horizon", "-"),
                row.get("priority", "-"),
                module_path,
                node_name.get(target_node, target_node),
                _short_text(str(row.get("why_now", "-")), limit=56),
                _short_text(str(row.get("done_when", "-")), limit=56),
            ]
        )

    lines = [
        "# Tool forest(Tool Forest)",
        "",
        GENERATED_NOTE,
        "",
        "## Understand at a glance",
        f"- Real number of modules:{len(real_rows)}",
        f"- Number of planning modules:{len(planned_rows)}",
        f"- Planning Execution Short Checklist:{backlog_count}",
        f"- Planning is not scheduled:{unscheduled_count}",
        f"- taxonomy Number of nodes:{len(taxonomy_nodes)}",
        (
            f"- real module role:canonical={role_count['canonical']},tool={role_count['tool']},"
            f"compat={role_count['compat']},bridge={role_count['bridge']},placeholder={role_count['placeholder']}"
        ),
        (
            f"- Real module proof status:proved={proof_count['proved']},statement={proof_count['statement']},"
            f"placeholder={proof_count['placeholder']}"
        ),
        "- `Books/Legacy` has been changed to `source_track` axis,No longer a main tree node.",
        "",
        "## view A:Taxonomy main tree",
        *view_a,
        "",
        "## surface 1:taxonomy Node overview",
        table(
            [
                "node_id",
                "node_name",
                "tier",
                "primary_parent_id",
                "real_modules",
                "planned_modules",
                "canonical",
                "tool",
            ],
            node_rows,
        ),
        "",
        "## surface 2:relationship edge(second father/association)",
        table(
            ["from_node", "from_name", "to_node", "to_name", "relation_type", "strength"],
            relation_rows,
        ),
        "",
        "## surface 3:source_track distributed(reality/planning)",
        table(
            ["source_track", "real_modules", "planned_modules"],
            source_rows,
        ),
        "",
        "## surface 4:Entry module(canonical + tool,Top 20)",
        f"- Total number of entries:{len(entry_rows_all)}(By default, only the front 20 strip,Please see the interactive page for details)",
        table(
            ["module_path", "node_name", "source_track", "layer", "role", "proof_status", "formal_decl_refs"],
            entry_rows,
        ),
        "",
        "## surface 5:Planning module sample(Top 12)",
        f"- Total number of planning modules:{len(planned_top_rows_all)}(Only the front is shown here 12 strip,Avoid swiping)",
        table(
            [
                "module_path",
                "target_node_name",
                "source_track",
                "status",
                "execution_horizon",
                "execution_priority",
                "reason",
            ],
            planned_top_rows,
        ),
        "",
        "## surface 6:Planning Execution Short Checklist(near/mid/far)",
        table(
            ["horizon", "priority", "module_path", "target_node", "why_now", "done_when"],
            backlog_rows[:10],
        ),
        "",
        "## interactive page(Full details)",
        "- See [ToolForestInteractive.html](./ToolForestInteractive.html).",
        "- By default, only the `real module`;Cut to it when needed `planning module`.",
        "- support `real module/planning module` switch,node/source/layer/role/proof/plan window Filter and search.",
        "- Want to quickly accept this round of changes:look [ReviewDashboard.md](./ReviewDashboard.md).",
        "- Want to quickly understand the purpose of the module:look [APICards.md](./APICards.md).",
        "",
        "## Instructions for use(people + Codex)",
        f"1. This document is provided by `{ 'docs/meta + artifacts/index' if source_mode == 'meta_index' else 'docs/ssot/registry.json' }` Automatically generated,Manual modification is prohibited.",
        "2. main tree view `taxonomy_nodes`,Looking at the horizontal relationship `taxonomy_relations`.",
        "3. Look at the real structure `modules`;Look at the road map `planned_modules`.",
        "4. Change process:",
        "- Change first `docs/ssot/registry.json`.",
        "- run `python3 tools/docs/validate_ssot.py`.",
        "- run `python3 tools/docs/sync_docs.py --write`.",
        "- run `python3 tools/ci/check_taxonomy_contract.py`.",
        "- run `python3 tools/ci/check_tool_forest_consistency.py`.",
        "",
    ]
    return "\n".join(lines)


def render_tool_forest_interactive(registry: dict) -> str:
    nodes, relations, real_rows, planned_rows, _ = _tool_forest_source(registry)
    payload = json.dumps(
        {
            "meta": registry["meta"],
            "nodes": nodes,
            "relations": relations,
            "modules": real_rows + planned_rows,
        },
        ensure_ascii=False,
    )

    html_template = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Tool Forest Interactive</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --card: #ffffff;
      --line: #d7deea;
      --text: #0f172a;
      --muted: #516078;
      --accent: #0f766e;
      --accent-soft: #e6f5f3;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "SF Pro Text", "PingFang SC", "Noto Sans CJK SC", sans-serif;
      color: var(--text);
      background: radial-gradient(1200px 700px at 10% -10%, #ebf4ff 0%, var(--bg) 45%);
    }}
    .wrap {{
      max-width: 1500px;
      margin: 0 auto;
      padding: 20px 18px 24px;
      display: grid;
      gap: 14px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 24px;
    }}
    .muted {{
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }}
    .chip {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 12px;
      background: #fff;
    }}
    .controls {{
      display: grid;
      grid-template-columns: 1.5fr repeat(7, minmax(110px, 1fr));
      gap: 8px;
      align-items: end;
    }}
    .controls label {{
      display: block;
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 4px;
    }}
    input, select, button {{
      width: 100%;
      padding: 8px 9px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: var(--text);
      font-size: 13px;
    }}
    button {{
      cursor: pointer;
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
      font-weight: 600;
    }}
    .qbtn {{
      width: auto;
      min-width: 140px;
      background: #fff;
      color: var(--text);
      border-color: var(--line);
    }}
    .layout {{
      display: grid;
      grid-template-columns: 34% 66%;
      gap: 12px;
      min-height: 640px;
    }}
    .tree {{
      max-height: 700px;
      overflow: auto;
      padding-right: 4px;
    }}
    details {{
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 8px 10px;
      margin-bottom: 8px;
      background: #fff;
    }}
    summary {{
      cursor: pointer;
      font-weight: 600;
      color: #16223a;
    }}
    .mini {{
      margin-top: 6px;
      font-size: 12px;
      color: var(--muted);
      line-height: 1.5;
    }}
    .group-list {{
      margin: 8px 0 0;
      padding-left: 16px;
      font-size: 12px;
      color: #1f2a40;
    }}
    .group-list li {{
      margin-bottom: 5px;
    }}
    .table-wrap {{
      max-height: 450px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 10px;
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }}
    th, td {{
      border-bottom: 1px solid #edf1f7;
      padding: 7px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      position: sticky;
      top: 0;
      z-index: 1;
      background: #f8fbff;
      font-size: 11px;
      color: #41516f;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    tr:hover {{
      background: var(--accent-soft);
      cursor: pointer;
    }}
    .detail {{
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px;
      min-height: 120px;
      background: #fff;
    }}
    .k {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 6px;
    }}
    .v {{
      font-size: 13px;
      margin-top: 2px;
      word-break: break-word;
    }}
    @media (max-width: 1024px) {{
      .controls {{
        grid-template-columns: 1fr 1fr;
      }}
      .layout {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Tool Forest Interactive</h1>
      <div class="muted">
        This page is read only `docs/ssot/registry.json` derived data.<br />
        By default, look at the real module first;Only switch to the planning module view when scheduling is needed.
      </div>
      <div class="chips" id="summary"></div>
    </div>

    <div class="card controls">
      <div>
        <label for="q">search</label>
        <input id="q" placeholder="module/node/subdomain/key_problem/formal decl" />
      </div>
      <div>
        <label for="f-dataset">Dataset</label>
        <select id="f-dataset">
          <option value="">all</option>
          <option value="real" selected>real module</option>
          <option value="planned">planning module</option>
        </select>
      </div>
      <div>
        <label for="f-node">Node</label>
        <select id="f-node"></select>
      </div>
      <div>
        <label for="f-layer">Layer</label>
        <select id="f-layer"></select>
      </div>
      <div>
        <label for="f-role">Role</label>
        <select id="f-role"></select>
      </div>
      <div>
        <label for="f-proof">Proof</label>
        <select id="f-proof"></select>
      </div>
      <div>
        <label for="f-plan-window">Plan Window</label>
        <select id="f-plan-window"></select>
      </div>
      <div>
        <label>&nbsp;</label>
        <button id="reset">Reset filter</button>
      </div>
    </div>

    <div class="card">
      <div class="muted" style="margin-bottom:6px;">quick view</div>
      <div class="chips">
        <button class="qbtn" id="preset-real">Only look at real modules</button>
        <button class="qbtn" id="preset-near">Only look at recent plans</button>
        <button class="qbtn" id="preset-all">Show all</button>
      </div>
    </div>

    <div class="layout">
      <div class="card">
        <div class="muted" style="margin-bottom:8px;">domain structure(Foldable)</div>
        <div class="tree" id="tree"></div>
      </div>
      <div class="card">
        <div class="muted" style="margin-bottom:8px;">Module list(Click on row to view details)</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>module_path</th>
                <th>node</th>
                <th>dataset</th>
                <th>source_track</th>
                <th>role</th>
                <th>layer</th>
                <th>proof</th>
              </tr>
            </thead>
            <tbody id="tbody"></tbody>
          </table>
        </div>
        <div class="detail" id="detail">
          <div class="muted">Click on any module row above to display details.</div>
        </div>
      </div>
    </div>
  </div>

  <script id="tool-forest-data" type="application/json">__TOOL_FOREST_PAYLOAD__</script>
  <script>
    const raw = JSON.parse(document.getElementById("tool-forest-data").textContent);
    const modules = raw.modules;
    const MAX_ROWS = 120;

    const dom = {{
      q: document.getElementById("q"),
      dataset: document.getElementById("f-dataset"),
      node: document.getElementById("f-node"),
      layer: document.getElementById("f-layer"),
      role: document.getElementById("f-role"),
      proof: document.getElementById("f-proof"),
      horizon: document.getElementById("f-plan-window"),
      reset: document.getElementById("reset"),
      presetReal: document.getElementById("preset-real"),
      presetNear: document.getElementById("preset-near"),
      presetAll: document.getElementById("preset-all"),
      summary: document.getElementById("summary"),
      tree: document.getElementById("tree"),
      tbody: document.getElementById("tbody"),
      detail: document.getElementById("detail"),
    }};

    function uniq(values) {{
      return [...new Set(values)].sort((a, b) => a.localeCompare(b, "zh"));
    }}

    function fillSelect(el, values) {{
      el.innerHTML = "";
      const opt0 = document.createElement("option");
      opt0.value = "";
      opt0.textContent = "all";
      el.appendChild(opt0);
      for (const v of values) {{
        const o = document.createElement("option");
        o.value = v;
        o.textContent = v;
        el.appendChild(o);
      }}
    }}

    fillSelect(dom.node, uniq(modules.map(m => m.node_name)));
    fillSelect(dom.layer, uniq(modules.map(m => m.layer)));
    fillSelect(dom.role, uniq(modules.map(m => m.role)));
    fillSelect(dom.proof, uniq(modules.map(m => m.proof_status)));
    fillSelect(
      dom.horizon,
      uniq(
        modules
          .filter(m => m.dataset === "planned")
          .map(m => m.execution_horizon)
      )
    );

    function filtered() {{
      const q = dom.q.value.trim().toLowerCase();
      return modules.filter(m => {{
        if (dom.dataset.value && m.dataset !== dom.dataset.value) return false;
        if (dom.node.value && m.node_name !== dom.node.value) return false;
        if (dom.layer.value && m.layer !== dom.layer.value) return false;
        if (dom.role.value && m.role !== dom.role.value) return false;
        if (dom.proof.value && m.proof_status !== dom.proof.value) return false;
        if (dom.horizon.value) {{
          if (m.dataset !== "planned") return false;
          if (m.execution_horizon !== dom.horizon.value) return false;
        }}
        if (!q) return true;
        const blob = [
          m.module_path, m.node_id, m.node_name, m.subdomain, m.key_problem, m.role, m.layer,
          m.proof_status, m.dataset, m.source_track, m.reason, m.execution_horizon,
          m.execution_priority, ...(m.formal_decl_refs || [])
        ].join(" ").toLowerCase();
        return blob.includes(q);
      }});
    }}

    function countBy(list, keyFn) {{
      const m = new Map();
      for (const x of list) {{
        const k = keyFn(x);
        m.set(k, (m.get(k) || 0) + 1);
      }}
      return m;
    }}

    function renderSummary(list) {{
      const role = countBy(list, x => x.role);
      const proof = countBy(list, x => x.proof_status);
      const shortlist = list.filter(x => x.in_backlog).length;
      const unscheduled = list.filter(x => x.execution_horizon === "unscheduled").length;
      dom.summary.innerHTML = "";
      const chips = [
        `modules=${list.length}`,
        `nodes=${new Set(list.map(x => x.node_name)).size}`,
        `real=${list.filter(x => x.dataset === "real").length}`,
        `planned=${list.filter(x => x.dataset === "planned").length}`,
        `shortlist=${shortlist}`,
        `unscheduled=${unscheduled}`,
        `canonical=${role.get("canonical") || 0}`,
        `tool=${role.get("tool") || 0}`,
        `compat=${role.get("compat") || 0}`,
        `planned-role=${role.get("planned") || 0}`,
        `proved=${proof.get("proved") || 0}`,
      ];
      for (const t of chips) {{
        const c = document.createElement("span");
        c.className = "chip";
        c.textContent = t;
        dom.summary.appendChild(c);
      }}
    }}

    function renderTree(list) {{
      const byDomain = new Map();
      for (const m of list) {{
        if (!byDomain.has(m.node_name)) byDomain.set(m.node_name, []);
        byDomain.get(m.node_name).push(m);
      }}
      const domains = [...byDomain.keys()].sort((a, b) => {
        const da = byDomain.get(a).length;
        const db = byDomain.get(b).length;
        if (db !== da) return db - da;
        return a.localeCompare(b, "zh");
      });
      dom.tree.innerHTML = "";

      for (const domain of domains) {{
        const ds = byDomain.get(domain);
        const subMap = new Map();
        for (const m of ds) {{
          if (!subMap.has(m.subdomain)) subMap.set(m.subdomain, []);
          subMap.get(m.subdomain).push(m);
        }}
        const d = document.createElement("details");
        d.open = ds.length <= 20;
        const s = document.createElement("summary");
        const canonical = ds.filter(x => x.role === "canonical").length;
        const tool = ds.filter(x => x.role === "tool").length;
        s.textContent = `${domain} (${ds.length}) | canonical:${canonical} tool:${tool}`;
        d.appendChild(s);

        const subs = [...subMap.keys()].sort((a, b) => {
          const sa = subMap.get(a).length;
          const sb = subMap.get(b).length;
          if (sb !== sa) return sb - sa;
          return a.localeCompare(b, "zh");
        });
        for (const sub of subs) {{
          const sMods = subMap.get(sub);
          const sd = document.createElement("details");
          sd.open = sMods.length <= 10;
          const ss = document.createElement("summary");
          ss.textContent = `${sub} (${sMods.length})`;
          sd.appendChild(ss);

          const pMap = new Map();
        for (const m of sMods) {{
          if (!pMap.has(m.key_problem)) pMap.set(m.key_problem, []);
          pMap.get(m.key_problem).push(m);
        }}
          const ul = document.createElement("ul");
          ul.className = "group-list";
          for (const p of [...pMap.keys()].sort((a, b) => {
            const pa = pMap.get(a).length;
            const pb = pMap.get(b).length;
            if (pb !== pa) return pb - pa;
            return a.localeCompare(b, "zh");
          })) {{
            const ms = pMap.get(p);
            const li = document.createElement("li");
            const c = ms.filter(x => x.role === "canonical").length;
            const t = ms.filter(x => x.role === "tool").length;
            li.textContent = `${p} (${ms.length})`;
            const subline = document.createElement("div");
            subline.className = "mini";
            subline.textContent = `source=${[...new Set(ms.map(x => x.source_track))].join(", ")} | canonical:${c} tool:${t}`;
            li.appendChild(subline);
            ul.appendChild(li);
          }}
          sd.appendChild(ul);
          d.appendChild(sd);
        }}
        dom.tree.appendChild(d);
      }}
    }}

    function renderTable(list) {{
      dom.tbody.innerHTML = "";
      const rows = list.slice(0, MAX_ROWS);
      for (const m of rows) {{
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${m.module_path}</td>
          <td>${m.node_name}</td>
          <td>${m.dataset}</td>
          <td>${m.source_track}</td>
          <td>${m.role}</td>
          <td>${m.layer}</td>
          <td>${m.proof_status}</td>
        `;
        tr.addEventListener("click", () => renderDetail(m));
        dom.tbody.appendChild(tr);
      }}
      if (list.length > MAX_ROWS) {{
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="7" class="muted">Shown before ${MAX_ROWS} strip,common ${list.length} strip.Please continue filtering or searching.</td>`;
        dom.tbody.appendChild(tr);
      }}
    }}

    function renderDetail(m) {{
      dom.detail.innerHTML = `
        <div class="k">module_path</div><div class="v">${m.module_path}</div>
        <div class="k">node / subdomain / key_problem</div><div class="v">${m.node_name} / ${m.subdomain} / ${m.key_problem}</div>
        <div class="k">dataset / source_track</div><div class="v">${m.dataset} / ${m.source_track}</div>
        <div class="k">plan window / priority / shortlist</div><div class="v">${m.execution_horizon || "-"} / ${m.execution_priority || "-"} / ${m.in_backlog ? "yes" : "no"}</div>
        <div class="k">layer / role / proof_status</div><div class="v">${m.layer} / ${m.role} / ${m.proof_status}</div>
        <div class="k">formal_decl_refs</div><div class="v">${(m.formal_decl_refs || []).join(", ") || "-"}</div>
        <div class="k">status</div><div class="v">${m.status || "-"}</div>
        <div class="k">reason</div><div class="v">${m.reason || "-"}</div>
      `;
    }}

    function rerender() {{
      const list = filtered();
      renderSummary(list);
      renderTree(list);
      renderTable(list);
    }}

    dom.q.addEventListener("input", rerender);
    dom.dataset.addEventListener("change", rerender);
    dom.node.addEventListener("change", rerender);
    dom.layer.addEventListener("change", rerender);
    dom.role.addEventListener("change", rerender);
    dom.proof.addEventListener("change", rerender);
    dom.horizon.addEventListener("change", rerender);
    dom.reset.addEventListener("click", () => {{
      dom.q.value = "";
      dom.dataset.value = "real";
      dom.node.value = "";
      dom.layer.value = "";
      dom.role.value = "";
      dom.proof.value = "";
      dom.horizon.value = "";
      rerender();
    }});

    dom.presetReal.addEventListener("click", () => {{
      dom.dataset.value = "real";
      dom.horizon.value = "";
      dom.q.value = "";
      rerender();
    }});

    dom.presetNear.addEventListener("click", () => {{
      dom.dataset.value = "planned";
      dom.horizon.value = "near";
      dom.q.value = "";
      rerender();
    }});

    dom.presetAll.addEventListener("click", () => {{
      dom.dataset.value = "";
      dom.horizon.value = "";
      dom.q.value = "";
      rerender();
    }});

    dom.dataset.value = "real";
    rerender();
  </script>
</body>
</html>
"""
    html = html_template.replace("{{", "{").replace("}}", "}")
    html = html.replace("__TOOL_FOREST_PAYLOAD__", payload)
    return html


def render_structure_cleanup_candidates(registry: dict) -> str:
    rows = []
    for item in registry["structure_cleanup_candidates"]:
        rows.append(
            [
                item["module_path"],
                item["definition_file"],
                "<br>".join(item["imported_by"]),
                item["role"],
                item["execution_state"],
                item["priority"],
                item["batch"],
                item["compatibility_window"],
                item["remove_after_releases"],
                item["migration_started_epoch"],
                "<br>".join(item["replacement_imports"]),
                item["risk"],
                item["suggested_action"],
            ]
        )

    if rows:
        intro_lines = [
            "1. This list is used for restructuring scheduling,Do not perform physical deletion this round.",
            "2. Each candidate must provide evidence:definition file + quilt import Location.",
            "3. `execution_state`:`pending` -> `deprecated_announced` -> `migrating` -> `ready_to_remove`.",
            "4. `remove_after_releases` + `migration_started_epoch` + `meta.cleanup_release_epoch` Decide whether to delete after expiration.",
            "5. This list is executed first `deprecated`,Physical deletion will not be evaluated until the compatibility window ends..",
            "6. You must write it before deleting it `DecisionLog`,And run full access control.",
        ]
    else:
        intro_lines = [
            "1. current `structure_cleanup_candidates=0`,Batch deletion of compatible portals has been completed.",
            "2. If a new compatible entry is added in the future,,Candidate evidence must be registered first,re-enter `deprecated -> ready_to_remove -> physical remove` process.",
            "3. The delete action still requires writing first `DecisionLog`,And run full access control.",
        ]

    return "\n".join(
        [
            "# Structural Cleanup Candidates(Just make a list)",
            "",
            GENERATED_NOTE,
            "",
            "## illustrate",
            *intro_lines,
            "",
            table(
                [
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
                ],
                rows,
            ),
            "",
        ]
    )


def render_namespace_convergence(registry: dict) -> str:
    modules = sorted(registry["modules"], key=lambda m: m["module_path"])
    aliases = sorted(registry["aliases"], key=lambda a: (a["status"], a["legacy_module"]))
    cleanup = registry["structure_cleanup_candidates"]

    layer_prefix = [
        ("core", "MLTheory.Core"),
        ("methods", "MLTheory.Methods"),
        ("applications", "MLTheory.Applications"),
        ("books", "MLTheory.Books"),
    ]

    prefix_rows = []
    for layer, prefix in layer_prefix:
        layer_modules = [m for m in modules if m["layer"] == layer]
        examples = [m["module_path"] for m in layer_modules[:3]]
        prefix_rows.append(
            [
                layer,
                prefix,
                len(layer_modules),
                "<br>".join(examples) if examples else "-",
            ]
        )

    legacy_root_rows = []
    for m in modules:
        if m["layer"] != "legacy":
            continue
        if m["module_path"].count(".") != 1:
            continue
        legacy_root_rows.append(
            [
                m["module_path"],
                m["source_track"],
                m["role"],
                m["status"],
                m["proof_status"],
            ]
        )

    deprecated_alias_rows = []
    active_alias_rows = []
    for a in aliases:
        row = [a["legacy_module"], a["canonical_module"], a["status"]]
        if a["status"] == "deprecated":
            deprecated_alias_rows.append(row)
        else:
            active_alias_rows.append(row)

    cleanup_summary = (
        "current `structure_cleanup_candidates = 0`,Batch deletion of compatible portals has been completed."
        if not cleanup
        else f"There are still {len(cleanup)} strip cleanup candidate,See details `StructureCleanupCandidates.md`."
    )

    return "\n".join(
        [
            "# Namespace convergence view(Namespace Convergence)",
            "",
            GENERATED_NOTE,
            "",
            "## Target(human language)",
            "1. New modules must fall under the hierarchical prefix(`Core/Methods/Applications/Books`).",
            "2. `legacy` Layers retain only top-level compatible entries(`MLTheory.X`),No more new depths legacy path.",
            "3. Map old entry paths to new entry paths via `aliases` to avoid"
            " 'imports still work, but migration targets are unclear'.",
            "",
            "## Current convergence status",
            f"- {cleanup_summary}",
            f"- Total number of real modules:{len(modules)}",
            f"- alias total:{len(aliases)}(deprecated={len(deprecated_alias_rows)} / active={len(active_alias_rows)})",
            "",
            "## Hierarchical prefix constraints(real module)",
            table(["layer", "required_prefix", "module_count", "examples"], prefix_rows),
            "",
            "## Remaining top layer legacy Entrance(Keep compatible)",
            table(
                ["module_path", "source_track", "role", "status", "proof_status"],
                legacy_root_rows,
            ),
            "",
            "## Deprecated Alias(old entrance -> new entrance)",
            table(["legacy_module", "canonical_module", "status"], deprecated_alias_rows),
            "",
            "## Active Alias(Still in compatibility mapping)",
            table(["legacy_module", "canonical_module", "status"], active_alias_rows),
            "",
        ]
    )


def render_gap_ledger(registry: dict) -> str:
    gaps = sorted(registry["gaps"], key=lambda g: (g["book"], g["chapter"], g["topic"]))
    rows = [
        [
            g["book"],
            g["chapter"],
            g["topic"],
            g["status"],
            g["last_search_date"],
            g["sources_checked"],
            g["candidate_repo"],
            g["next_action"],
        ]
        for g in gaps
    ]
    return "\n".join(
        [
            "# Global gap ledger(Gap Ledger)",
            "",
            GENERATED_NOTE,
            "",
            "Field constraints:`book`,`chapter`,`topic`,`status`,`last_search_date`,`sources_checked`,`candidate_repo`,`next_action`",
            "",
            table(
                [
                    "book",
                    "chapter",
                    "topic",
                    "status",
                    "last_search_date",
                    "sources_checked",
                    "candidate_repo",
                    "next_action",
                ],
                rows,
            ),
            "",
        ]
    )


def render_book_doc(book: dict, last_updated: str) -> str:
    def _row_value(row: dict, en_key: str, zh_key: str) -> str:
        return str(row.get(en_key, row.get(zh_key, "")))

    lines = []
    lines.append(f"# {book['title']} overlay mapping")
    lines.append("")
    lines.append(GENERATED_NOTE)
    lines.append("")
    lines.append("## bibliographic information")
    lines.append(f"- book title:{book['title']}")
    lines.append(f"- Version:{book['edition']}")
    lines.append(f"- Coverage date:{last_updated}")
    lines.append("- maintainer:Codex + user")
    lines.append("")
    lines.append("## Table of Contents Sources and Evidence")
    if book["evidence_links"]:
        for i, link in enumerate(book["evidence_links"], start=1):
            lines.append(f"{i}. `{link}`")
    else:
        lines.append("1. (No external URL;See the description of evidence in the corresponding chapter)")
    lines.append("")
    lines.append("## Chapter coverage table(SSOT derived)")
    rows = [
        [
            _row_value(r, "chapter", "\u7ae0\u8282"),
            _row_value(r, "module", "\u5bf9\u5e94\u6a21\u5757"),
            _row_value(r, "status", "\u8986\u76d6\u72b6\u6001"),
            _row_value(r, "evidence_link", "\u8bc1\u636e\u94fe\u63a5"),
            _row_value(r, "gap_note", "\u7f3a\u53e3\u8bf4\u660e"),
            _row_value(r, "next_action", "\u540e\u7eed\u52a8\u4f5c"),
        ]
        for r in book["coverage_rows"]
    ]
    lines.append(
        table(
            ["chapter", "Corresponding module", "Override status", "Evidence link", "Gap description", "Follow-up actions"],
            rows,
        )
    )
    lines.append("")
    lines.append("## Linked to global documents")
    lines.append("1. The module path starts with `../ModuleCatalog.md` as the only module manifest source.")
    lines.append("2. Gap tracking starts with `../GapLedger.md` It is the only source of gap ledger.")
    lines.append("3. This file only retains chapter coverage mapping,No repeated maintenance of the full module table.")
    lines.append("")
    return "\n".join(lines)


def render_books_readme(registry: dict) -> str:
    rows = []
    for book in registry["books"]:
        rel = Path(book["doc_file"]).name
        rows.append(
            [
                book["title"],
                f"[{rel}](./{rel})",
                f"[../GapLedger.md](../GapLedger.md)(`book={book['book_id']}`)",
            ]
        )

    return "\n".join(
        [
            "# book coverage index",
            "",
            GENERATED_NOTE,
            "",
            "## Overwrite document",
            table(["books", "Overwrite document", "Source of gap"], rows),
            "",
            "## template",
            "- [Next book coverage template](./_BookCoverageTemplate.md)",
            "",
            "## Usage convention",
            "1. Each book first drops coverage documents,Fill in the gaps.",
            "2. Only three gears are used for coverage status.:`covered`,`partial`,`gap`(allow `planned` Only for chapters that have not yet been completed).",
            "3. The module name in the document must match `../ModuleCatalog.md` of `module_path` consistent.",
            "",
        ]
    )


def render_glossary() -> str:
    return "\n".join(
        [
            "# Glossary of vernacular terms(Glossary)",
            "",
            GENERATED_NOTE,
            "",
            "## Data structure basics",
            "1. JSON:a data format,expressible objects(key value pair)and array(list).",
            "2. root(outermost layer):JSON The outermost object of the file.",
            "3. object(object):shaped like `{ \"key\": value }`.",
            "4. array(array):shaped like `[value1, value2, ...]`.",
            "",
            "## SSOT root field(`docs/ssot/registry.json`)",
            "1. `meta`:Global project information(language,toolchain,Update time,Strategy,cleanup_release_epoch).",
            "2. `decisions`:Decision log(date,decision making,state,Influence).",
            "3. `taxonomy_nodes`:main tree node(master-father relationship + tier Label).",
            "4. `taxonomy_relations`:Horizontal relationship edge(second father/association + strength 0~1).",
            "5. `official_workflow_refs`:Lean Official workflow capabilities and warehouse location mapping.",
            "6. `canonical_specs`:canonical Entrance contract(sign/forbidden words/Dependency closure).",
            "7. `modules`:Real module list(Must have local `.lean` document).",
            "8. `planned_modules`:Planning module list(Allow files that have not been implemented yet).",
            "9. `execution_backlog`:Planning short list(`near/mid/far` + priority + complete definition).",
            "10. `structure_cleanup_candidates`:Restructuring Candidates(Execution status,in batches,Compatibility window,window value,Migration starting point,alternative entrance,risk,Recommended action).",
            "11. `gaps`:Gap ledger(Topics not covered or partially covered and follow-up actions).",
            "12. `books`:book coverage mapping(chapter -> module -> Override status).",
            "13. `aliases`:Compatible mapping(old module path -> new module path).",
            "",
            "## Module related terms",
            "1. module(module):one can be `import` of Lean code unit,Usually corresponds to a `.lean` document.",
            "2. `module_path`:module path,like `MLTheory.Core.Learning.PAC`.",
            "3. `status`:Override status,`planned/partial/covered/gap`.",
            "3.1 In `planned_modules`, `partial` is only allowed for entries with traceable external evidence;"
            " otherwise use `planned` or `gap`.",
            "4. `primary_node_id`:module in taxonomy Primary home node in the primary tree.",
            "5. `source_track`:source axis(`native/books/legacy`).",
            "5.1 exist `modules` Desirable `native/books/legacy`;exist `planned_modules` Only allowed in `native/books`.",
            "5.2 `execution_backlog` used to give `planned_modules` Do short queue scheduling:`near`(Recently),`mid`(medium term),`far`(forward).",
            "6. `layer`:Hierarchical ownership,`core/methods/applications/books/legacy`.",
            "7. `proof_status`:Demonstrate progress,`placeholder/statement/proved`.",
            "8. `placeholder_policy_scope`:placeholder strategy,`allowed/forbidden`.",
            "9. `role`:module role(canonical/compat/bridge/tool/placeholder).",
            "10. `user_surface`:Whether to be a public entrance to users(public/internal).",
            "11. `formal_decl_refs`:List of key declaration names carried by this module.",
            "",
            "## Documentation generation and consistency",
            "1. SSOT(Single Source of Truth):single source of truth,here it is `docs/ssot/registry.json`.",
            "2. Derived documents:from SSOT automatically generated Markdown(like `INDEX.md`,`ModuleCatalog.md`).",
            "3. `sync_docs.py --write`:Generate documents according to fixed template.",
            "4. `sync_docs.py --check`: regenerate expected text and compare it to the current file;"
            " any difference fails the check.",
            "5. fixed template:`tools/docs/sync_docs.py` inside `render_*` function(title,Column order,The descriptions are all written down).",
            "6. `NamespaceConvergence.md`:Namespace convergence view(Too SSOT derived,Manual modification is not allowed).",
            "",
            "## Lean Build and check",
            "1. `lake build`:build the entire Lean project(parse import,type checking,Generate products).",
            "2. `import`:Import module.",
            "3. `#check`:Check if a name exists,Is the type correct?.",
            "4. smoke check(smoke):Quickly confirm that critical paths can still be compiled with a minimal example.",
            "",
            "## Quality Gate Control Script",
            "1. `check_no_sorry_axiom.sh`:Does the scan appear? `sorry` or `axiom`.",
            "2. `sorry`:Temporary placeholder,Indicates that the proof is not completed but the compilation must pass first.",
            "3. `axiom`:Direct introduction of unproven premises,Will reduce formal reliability.",
            "4. `check_placeholder_policy.sh`:examine `Core/Methods` not allowed `Prop := True` Placeholder,and check SSOT placeholder policy field.",
            "5. Allowable range of space occupied:Current policy allows `applications/books/legacy` Keep staged placeholders,not allowed `core/methods` placeholder return.",
            "6. `check_canonical_contract.sh`:examine canonical contract declares existence,Forbidden words and dependent citations.",
            "7. `check_official_workflow_alignment.sh`:Check official capability mapping(Loogle/LeanSearch/InfoView/LoogleView/REPL).",
            "8. `check_tool_forest_consistency.py`:Check concept tree and module ownership consistency.",
            "9. `check_review_views_consistency.py`:examine ReviewDashboard/APICards/Is the default behavior of interactive pages consistent with SSOT consistent.",
            "10. `check_namespace_layout.py`:Check that module paths respect hierarchical prefixes with alias Convergence constraints.",
            "11. `check_no_new_deprecated_imports.sh`:Prohibit new additions to deprecated compatible entries import(Backflow prevention).",
            "12. `check_ready_to_remove.py`:according to release The window automatically determines whether to enter `ready_to_remove`.",
            "13. `check_registry_reference_hygiene.py`:examine books/gaps Whether to quote deprecated alias,and check coverage Whether there are repeated modules in the row.",
            "14. `check_ssot_migration_idempotent.sh`:Check migration script idempotence(current registry MUST NOT produce after running migration diff).",
            "15. `advance_cleanup_release_epoch.py`:advance cleanup_release_epoch And automatically switch to the expiration candidate status.",
            "16. `StructureCleanupCandidates.md`:Restructuring candidate list(This round only list,Don't delete files).",
            "",
            "## Compatibility layer and import regression",
            "1. Compatibility layer:Thin wrapper files for old module paths,for keeping history `import` constantly.",
            "2. thin package:The file itself does not host the core implementation,Mainly forwarded to the new hierarchical module.",
            "3. Import regression:`Eval/ImportSmoke.lean` Import new path and old path at the same time,Verify that the interface is not broken after reconstruction.",
            "",
            "## Development environment terminology",
            "1. symlink(symbolic link):Similar shortcut,Point to another directory or file.",
            "2. submodule(Git submodule):Fixed reference to a commit in another repository in one repository.",
            "3. MCP:Codex Tool service access layer used;For this project `lean-lsp-mcp` supply Lean Interactive capabilities.",
            "",
            "## Common commands(Main warehouse)",
            "1. `python3 tools/docs/validate_ssot.py`",
            "2. `python3 tools/docs/sync_docs.py --check`",
            "3. `python3 tools/docs/sync_docs.py --write`",
            "4. `tools/ci/check_no_sorry_axiom.sh`",
            "5. `tools/ci/check_placeholder_policy.sh`",
            "6. `tools/ci/check_canonical_contract.sh`",
            "7. `tools/ci/check_official_workflow_alignment.sh`",
            "8. `python3 tools/ci/check_tool_forest_consistency.py`",
            "9. `python3 tools/ci/check_review_views_consistency.py`",
            "10. `python3 tools/ci/check_namespace_layout.py`",
            "11. `tools/ci/check_no_new_deprecated_imports.sh`",
            "12. `python3 tools/ci/check_ready_to_remove.py`",
            "13. `python3 tools/ci/check_registry_reference_hygiene.py`",
            "14. `tools/ci/check_ssot_migration_idempotent.sh`",
            "15. `python3 tools/ci/advance_cleanup_release_epoch.py --to <N> --write`",
            "16. `~/.elan/bin/lake env lean Eval/ImportSmoke.lean`",
            "17. `~/.elan/bin/lake build`",
            "",
            "## Common errors(meaning -> Suggested command)",
            "| Error report fragment | meaning(vernacular) | Which command to run first? |",
            "|---|---|---|",
            "| `Derived docs are out of sync` | The generated document is inconsistent with the existing document in the warehouse | `python3 tools/docs/sync_docs.py --write` Then `--check` |",
            "| `missing keys` / `extra keys` | `registry.json` Field does not conform to contract | `python3 tools/docs/validate_ssot.py` Repair after positioning JSON Field |",
            "| `bad import` | The import path is invalid or the dependencies are not pulled locally. | First `~/.elan/bin/lake build`,Check the correspondence again `import` Does the path exist? |",
            "| `found forbidden token` | Prohibited `sorry/axiom` | `tools/ci/check_no_sorry_axiom.sh` Locate and delete |",
            "| `Prop := True placeholders` | `Core/Methods` An illegal placeholder appears | `tools/ci/check_placeholder_policy.sh` locate and change to true statement |",
            "| `no such file or directory`(mathlib) | Dependency directory or path does not match | `~/.elan/bin/lake build` Re-parse dependencies and look at the first failure point |",
            "",
            "## Terminology back-checking(How to find the definition when you see a new word)",
            "1. first `docs/Glossary.md` Look at the vernacular definition.",
            "2. again `docs/ssot/registry.json` Check the field or module path corresponding to the word.",
            "3. If it is the module name(like `MLTheory.X.Y`),use `rg \"MLTheory\\.X\\.Y\" docs /Users/xiongjiangkai/xjk_papers/MLTheory/MLTheory` Find sources and citations.",
            "4. If it is a script term(like `placeholder_policy_scope`),use `rg \"placeholder_policy_scope\" /Users/xiongjiangkai/xjk_papers/MLTheory/tools` Find verification logic.",
            "5. if CI the term(like `ImportSmoke`),look `/Users/xiongjiangkai/xjk_papers/MLTheory/.github/workflows/lean_action_ci.yml` Corresponding steps.",
            "6. If still unclear, ask: 'In which file and line does this term take effect?'"
            " to avoid semantic ambiguity.",
            "",
        ]
    )


def render_index(registry: dict) -> str:
    book_rows = []
    for book in registry["books"]:
        rel = Path(book["doc_file"]).name
        book_rows.append([book["title"], f"[books/{rel}](./books/{rel})"])

    return "\n".join(
        [
            "# MLTheory Document index",
            "",
            GENERATED_NOTE,
            "",
            "## Purpose",
            "This directory is used for precipitation MLTheory historical decisions,Module planning,Book coverage and gap search ledger.",
            "",
            "## core navigation",
            "<!-- AUTO:INDEX-CORE-NAV BEGIN -->",
            table(
                ["document", "illustrate"],
                [
                    ["[../AGENTS.md](../AGENTS.md)", "Agent execution specifications(Document system first,Delete legacy rules)"],
                    ["[DecisionLog.md](./DecisionLog.md)", "Decision log(fixed fields:`date/decision/status/impact`)"],
                    ["[ModuleCatalog.md](./ModuleCatalog.md)", "Module summary(fixed fields:`module_path/primary_node_id/source_track/status/...`)"],
                    ["[GapLedger.md](./GapLedger.md)", "Global gap ledger(fixed fields:`book/chapter/topic/status/last_search_date/sources_checked/candidate_repo/next_action`)"],
                    ["[ToolForest.md](./ToolForest.md)", "concept + Module forest diagram(Depend on SSOT Automatically generated)"],
                    ["[ToolForestInteractive.html](./ToolForestInteractive.html)", "filterable/Searchable/Collapsible interactive structure view(Recommended for daily use)"],
                    ["[GraphExplorer.html](./GraphExplorer.html)", "Graph view MVP(Backbone priority + One jump to expand,read subgraph)"],
                    ["[ReviewDashboard.md](./ReviewDashboard.md)", "Acceptance Kanban(New in this round,current focus,One-click acceptance command)"],
                    ["[RefactorHandoffForGPT52Pro.md](./RefactorHandoffForGPT52Pro.md)", "Give GPT5.2pro refactoring handover package(Achieve panorama + access control + risk)"],
                    ["[APICards.md](./APICards.md)", "smallest API card(each public what module does,Which statements to look at first)"],
                    ["[ExecutionBacklog.md](./ExecutionBacklog.md)", "Planning module short list(near/mid/far),Bundle 96 roadmap converges into executable queue"],
                    ["[NamespaceConvergence.md](./NamespaceConvergence.md)", "Namespace convergence view(Level prefix,legacy Entrance,alias mapping)"],
                    ["[StructureIssues.md](./StructureIssues.md)", "Structural Issues Ledger(Automatically identify problems + Rectification order in batches + rollback point)"],
                    ["[StructureCleanupCandidates.md](./StructureCleanupCandidates.md)", "Restructuring candidate list(in batches/window/alternative entrance/risk)"],
                    ["[books/README.md](./books/README.md)", "Books cover index page"],
                    ["[Glossary.md](./Glossary.md)", "Glossary of vernacular terms(Reduce slang communication costs)"],
                    ["[meta/taxonomy.yaml](./meta/taxonomy.yaml)", "vNext Concept tree and binding(Increment meta)"],
                    ["[meta/aliases.yaml](./meta/aliases.yaml)", "vNext Retrieve alias table(Increment meta)"],
                    ["[meta/canon.yaml](./meta/canon.yaml)", "vNext Stablize API Checklist(Increment meta)"],
                    ["[meta/backlog.yaml](./meta/backlog.yaml)", "Optional blueprint-style Spec execution backlog states"],
                    ["[meta/ui.yaml](./meta/ui.yaml)", "Optional graph viewer defaults(scope/spine/expand/visible nodes)"],
                    ["[_auto/README.md](./_auto/README.md)", "AutoView Catalog Description(Generate entry)"],
                    ["[_auto/CodeIndex.md](./_auto/CodeIndex.md)", "code first module/import automatic view"],
                    ["[_auto/GraphArtifacts.md](./_auto/GraphArtifacts.md)", "subgraph with telemetry Statistics automatic view"],
                    ["[ssot/registry.json](./ssot/registry.json)", "single source of truth(The only data file that can be modified manually)"],
                    ["[ssot/schema.json](./ssot/schema.json)", "SSOT field contract"],
                ],
            ),
            "<!-- AUTO:INDEX-CORE-NAV END -->",
            "",
            "## Book coverage document",
            "<!-- AUTO:INDEX-BOOKS BEGIN -->",
            table(["books", "Overwrite document"], book_rows),
            "<!-- AUTO:INDEX-BOOKS END -->",
            "",
            "## maintenance rules(When adding a new book)",
            "1. Update first `ssot/registry.json`,Run the document generation script again.",
            "2. implement `python3 tools/docs/validate_ssot.py` Check field contract.",
            "3. implement `python3 tools/docs/sync_docs.py --write` Generate derived documents.",
            "4. implement `tools/index/gen_mltheory_index.sh` renew `artifacts/index` and `docs/_auto`.",
            "5. If deleted or replaced,must be in `DecisionLog.md` leave traces.",
            "",
            "## ToolForest Get started quickly",
            "1. Accept the current round of changes:Look first [ReviewDashboard.md](./ReviewDashboard.md).",
            "2. To give complete context to the reconstructed model:look [RefactorHandoffForGPT52Pro.md](./RefactorHandoffForGPT52Pro.md).",
            "3. See module usage and entry declaration:Look again [APICards.md](./APICards.md).",
            "4. Look at the overall structure:Open [ToolForestInteractive.html](./ToolForestInteractive.html)(By default, only the real modules are viewed).",
            "5. Look at the backbone+Expand map:Open [GraphExplorer.html](./GraphExplorer.html).",
            "6. Look at index statistics and graph statistics:Check [_auto/CodeIndex.md](./_auto/CodeIndex.md) + [_auto/GraphArtifacts.md](./_auto/GraphArtifacts.md).",
            "7. To overview the main tree, read [ToolForest.md](./ToolForest.md), Table 1: taxonomy node overview.",
            "8. Depends on the recent schedule:look [ExecutionBacklog.md](./ExecutionBacklog.md).",
            "9. Depends on the namespace migration path:look [NamespaceConvergence.md](./NamespaceConvergence.md).",
            "10. Depends on structural issues and cleanup candidates:look [StructureIssues.md](./StructureIssues.md) + [StructureCleanupCandidates.md](./StructureCleanupCandidates.md).",
            "11. Any structural adjustment can only change `ssot/registry.json`,Execute again:",
            "- `python3 tools/docs/validate_ssot.py`",
            "- `python3 tools/docs/sync_docs.py --write`",
            "- `tools/index/gen_mltheory_index.sh`",
            "- `tools/index/gen_graph_artifacts.sh`",
            "- `python3 tools/ci/check_taxonomy_contract.py`",
            "- `python3 tools/ci/check_tool_forest_consistency.py`",
            "- `python3 tools/ci/check_review_views_consistency.py`",
            "- `python3 tools/ci/check_namespace_layout.py`",
            "- `tools/ci/check_ssot_migration_idempotent.sh`",
            "- `tools/ci/check_no_new_deprecated_imports.sh`",
            "- `python3 tools/ci/check_ready_to_remove.py`",
            "- `python3 tools/ci/check_registry_reference_hygiene.py`",
            "",
            "## Current default constraints",
            "1. Document language:Chinese.",
            "2. Document organization:Multiple document indexing(Not merged into a single overall document).",
            "3. Near term strategy:Stable first SSOT with layered module skeleton,Then add proof chapter by chapter.",
            "4. delete rule:Random deletion is not allowed;When deletion is justified, the scope of impact must be recorded.",
            "",
        ]
    )


def render_book_template() -> str:
    return "\n".join(
        [
            "# book cover template(Rename after copying)",
            "",
            GENERATED_NOTE,
            "",
            "## bibliographic information",
            "- book title:",
            "- Version:",
            "- Coverage date:",
            "- maintainer:",
            "",
            "## Chapter coverage table",
            "| chapter | Corresponding module | Override status | Evidence link | Gap description | Follow-up actions |",
            "|---|---|---|---|---|---|",
            "| Example:Ch1 | `MLTheory.XXX.YYY` | partial | `https://...` | missing a theorem | Add a placeholder in a module and continue searching |",
            "",
            "## Override status definition",
            "- `covered`:Already available for direct reuse Lean formal content.",
            "- `partial`:There are infrastructure or external candidates,But the chapter is not completely covered.",
            "- `gap`:There is currently no reusable formal implementation.",
            "",
            "## Linked to global documents",
            "1. After adding this book document,Must update:",
            "- `../README.md`(book index)",
            "- `../../ModuleCatalog.md`(`book_refs`)",
            "- `../../GapLedger.md`(gap entry)",
            "- `../../DecisionLog.md`(Key strategy changes)",
            "",
            "2. Record granularity requirements:",
            "- each gap Required `last_search_date` and `next_action`.",
            "- The module name must match `ModuleCatalog.md` of `module_path` completely consistent.",
            "",
        ]
    )


def render_all(registry: dict) -> dict[Path, str]:
    files: dict[Path, str] = {}
    files[ROOT / "docs" / "DecisionLog.md"] = render_decision_log(registry)
    files[ROOT / "docs" / "ModuleCatalog.md"] = render_module_catalog(registry)
    files[ROOT / "docs" / "GapLedger.md"] = render_gap_ledger(registry)
    files[ROOT / "docs" / "ToolForest.md"] = render_tool_forest(registry)
    files[ROOT / "docs" / "ToolForestInteractive.html"] = render_tool_forest_interactive(registry)
    files[ROOT / "docs" / "ReviewDashboard.md"] = render_review_dashboard(registry)
    files[ROOT / "docs" / "RefactorHandoffForGPT52Pro.md"] = render_refactor_handoff(registry)
    files[ROOT / "docs" / "APICards.md"] = render_api_cards(registry)
    files[ROOT / "docs" / "ExecutionBacklog.md"] = render_execution_backlog(registry)
    files[ROOT / "docs" / "NamespaceConvergence.md"] = render_namespace_convergence(registry)
    files[ROOT / "docs" / "StructureIssues.md"] = render_structure_issues(registry)
    files[ROOT / "docs" / "StructureCleanupCandidates.md"] = render_structure_cleanup_candidates(registry)
    files[ROOT / "docs" / "Glossary.md"] = render_glossary()
    files[ROOT / "docs" / "books" / "README.md"] = render_books_readme(registry)
    files[ROOT / "docs" / "INDEX.md"] = render_index(registry)
    files[ROOT / "docs" / "books" / "_BookCoverageTemplate.md"] = render_book_template()

    for book in registry["books"]:
        doc_path = ROOT / book["doc_file"]
        files[doc_path] = render_book_doc(book, registry["meta"]["last_updated"])

    for path, content in list(files.items()):
        files[path] = _wrap_generated_doc_with_auto_block(path, content)

    return files


def check_mode(outputs: dict[Path, str]) -> int:
    mismatches: list[Path] = []
    for path, content in outputs.items():
        expected = content
        if not path.exists():
            mismatches.append(path)
            continue
        current = path.read_text(encoding="utf-8")
        expected = _merge_auto_blocks(current, content)
        if current != expected:
            mismatches.append(path)
    if mismatches:
        print("Derived docs are out of sync:")
        for path in mismatches:
            print(f"- {path.relative_to(ROOT)}")
        return 1
    print(f"Derived docs are in sync ({len(outputs)} files).")
    return 0


def write_mode(outputs: dict[Path, str]) -> int:
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            current = path.read_text(encoding="utf-8")
            content = _merge_auto_blocks(current, content)
        path.write_text(content, encoding="utf-8")
    print(f"Generated {len(outputs)} files from SSOT.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate docs from SSOT registry.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="write derived files")
    group.add_argument("--check", action="store_true", help="check if derived files are up to date")
    args = parser.parse_args()

    registry = load_registry()
    outputs = render_all(registry)

    if args.check:
        return check_mode(outputs)
    return write_mode(outputs)


if __name__ == "__main__":
    sys.exit(main())
