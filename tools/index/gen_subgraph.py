#!/usr/bin/env python3
"""Generate merged subgraph artifact from module/decl/usage/meta layers."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                out.append(row)
    return out


def parse_scalar(raw: str):
    text = raw.strip()
    if text == "null":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if text.isdigit():
        return int(text)
    return text.strip('"').strip("'")


def parse_simple_yaml(path: Path) -> dict:
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
                    if section in {"nodes", "bindings"}:
                        result[section] = []
                    else:
                        result[section] = {}
                continue

            if section in {"nodes", "bindings"}:
                if stripped.startswith("- "):
                    if current is not None:
                        result[section].append(current)
                    current = {}
                    tail = stripped[2:].strip()
                    if ":" in tail:
                        k, v = tail.split(":", 1)
                        current[k.strip()] = parse_scalar(v)
                    continue
                if current is not None and ":" in stripped:
                    k, v = stripped.split(":", 1)
                    current[k.strip()] = parse_scalar(v)
                continue

            if section is not None and isinstance(result.get(section), dict) and ":" in stripped:
                k, v = stripped.split(":", 1)
                key = k.strip()
                val = v.strip()
                if val == "":
                    result[section][key] = []
                else:
                    result[section][key] = parse_scalar(val)
                continue

            if section is not None and isinstance(result.get(section), dict) and stripped.startswith("- "):
                val = parse_scalar(stripped[2:])
                # Append to the latest key of this mapping section.
                keys = list(result[section].keys())
                if keys:
                    result[section][keys[-1]].append(val)

    if section in {"nodes", "bindings"} and current is not None:
        result.setdefault(section, []).append(current)
    return result


def load_canon(path: Path) -> tuple[set[str], set[str]]:
    data = parse_simple_yaml(path)
    mods = set()
    decls = set()
    for v in data.get("canonical_modules", []):
        if isinstance(v, str):
            mods.add(v)
    for v in data.get("canonical_decls", []):
        if isinstance(v, str):
            decls.add(v)
    return mods, decls


def as_str_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [x for x in value if isinstance(x, str) and x]


def load_domain_profiles_legacy(path: Path) -> dict:
    data = parse_simple_yaml(path)

    def section(name: str) -> dict:
        sec = data.get(name)
        return sec if isinstance(sec, dict) else {}

    titles = section("domain_titles")
    descriptions = section("domain_descriptions")
    module_roots = section("domain_module_roots")
    allowed_local_roots = section("domain_allowed_local_roots")
    concept_binds = section("domain_concept_binds")
    default_imports = section("domain_default_imports")
    mathlib_slice_roots = section("domain_mathlib_slice_roots")
    skills_whitelist = section("domain_skills_whitelist")
    bridge_modules = section("domain_bridge_modules")
    adjacent_domains = section("domain_adjacent_domains")

    domain_ids: set[str] = set()
    for sec in (
        titles,
        descriptions,
        module_roots,
        allowed_local_roots,
        concept_binds,
        default_imports,
        mathlib_slice_roots,
        skills_whitelist,
        bridge_modules,
        adjacent_domains,
    ):
        domain_ids.update(k for k in sec if isinstance(k, str) and k)

    profiles: dict[str, dict] = {}
    for domain_id in sorted(domain_ids):
        title_raw = titles.get(domain_id, domain_id)
        desc_raw = descriptions.get(domain_id, "")
        profiles[domain_id] = {
            "id": domain_id,
            "title": title_raw if isinstance(title_raw, str) else domain_id,
            "description": desc_raw if isinstance(desc_raw, str) else "",
            "module_roots": as_str_list(module_roots.get(domain_id)),
            "allowed_local_roots": as_str_list(allowed_local_roots.get(domain_id)),
            "concept_binds": as_str_list(concept_binds.get(domain_id)),
            "default_imports": as_str_list(default_imports.get(domain_id)),
            "mathlib_slice_roots": as_str_list(mathlib_slice_roots.get(domain_id)),
            "skills_whitelist": as_str_list(skills_whitelist.get(domain_id)),
            "bridge_modules": as_str_list(bridge_modules.get(domain_id)),
            "adjacent_domains": as_str_list(adjacent_domains.get(domain_id)),
        }

    default_domain = data.get("default_domain")
    if path.exists() and (not isinstance(default_domain, str) or not default_domain):
        with path.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("default_domain:"):
                    default_domain = parse_scalar(line.split(":", 1)[1])
                    break
    if not isinstance(default_domain, str) or default_domain not in profiles:
        default_domain = "all"

    return {
        "default_domain": default_domain,
        "profiles": profiles,
        "source": str(path),
    }


def load_axis_taxonomy(path: Path, axis: str) -> dict:
    data = parse_simple_yaml(path)

    def section(name: str) -> dict:
        sec = data.get(name)
        return sec if isinstance(sec, dict) else {}

    titles = section("tag_titles")
    descriptions = section("tag_descriptions")
    module_roots = section("tag_module_roots")
    path_roots = section("tag_path_roots")
    mathlib_roots = section("tag_mathlib_roots")
    concept_binds = section("tag_concept_binds")
    adjacent_tags = section("tag_adjacent_tags")

    tag_ids: set[str] = set()
    for sec in (
        titles,
        descriptions,
        module_roots,
        path_roots,
        mathlib_roots,
        concept_binds,
        adjacent_tags,
    ):
        tag_ids.update(k for k in sec if isinstance(k, str) and k)

    tags: dict[str, dict] = {}
    for tag_id in sorted(tag_ids):
        title_raw = titles.get(tag_id, tag_id)
        desc_raw = descriptions.get(tag_id, "")
        tags[tag_id] = {
            "id": tag_id,
            "title": title_raw if isinstance(title_raw, str) else tag_id,
            "description": desc_raw if isinstance(desc_raw, str) else "",
            "module_roots": as_str_list(module_roots.get(tag_id)),
            "path_roots": as_str_list(path_roots.get(tag_id)),
            "mathlib_roots": as_str_list(mathlib_roots.get(tag_id)),
            "concept_binds": as_str_list(concept_binds.get(tag_id)),
            "adjacent_tags": as_str_list(adjacent_tags.get(tag_id)),
        }

    default_tag = data.get("default_tag")
    if path.exists() and (not isinstance(default_tag, str) or not default_tag):
        with path.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("default_tag:"):
                    default_tag = parse_scalar(line.split(":", 1)[1])
                    break
    if not isinstance(default_tag, str) or default_tag not in tags:
        default_tag = "all"

    return {
        "axis": axis,
        "default_tag": default_tag,
        "tags": tags,
        "source": str(path),
    }


def load_profile_axes(path: Path) -> dict:
    data = parse_simple_yaml(path)

    def section(name: str) -> dict:
        sec = data.get(name)
        return sec if isinstance(sec, dict) else {}

    titles = section("profile_titles")
    descriptions = section("profile_descriptions")
    math_tags = section("profile_math_tags")
    applied_tags = section("profile_applied_tags")
    adjacent_profiles = section("profile_adjacent_profiles")

    profile_ids: set[str] = set()
    for sec in (titles, descriptions, math_tags, applied_tags, adjacent_profiles):
        profile_ids.update(k for k in sec if isinstance(k, str) and k)

    profiles: dict[str, dict] = {}
    for profile_id in sorted(profile_ids):
        title_raw = titles.get(profile_id, profile_id)
        desc_raw = descriptions.get(profile_id, "")
        profiles[profile_id] = {
            "id": profile_id,
            "title": title_raw if isinstance(title_raw, str) else profile_id,
            "description": desc_raw if isinstance(desc_raw, str) else "",
            "math_tags": as_str_list(math_tags.get(profile_id)),
            "applied_tags": as_str_list(applied_tags.get(profile_id)),
            "adjacent_profiles": as_str_list(adjacent_profiles.get(profile_id)),
        }

    default_profile = data.get("default_profile")
    if path.exists() and (not isinstance(default_profile, str) or not default_profile):
        with path.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("default_profile:"):
                    default_profile = parse_scalar(line.split(":", 1)[1])
                    break
    if not isinstance(default_profile, str) or default_profile not in profiles:
        default_profile = "all"

    return {
        "default_profile": default_profile,
        "profiles": profiles,
        "source": str(path),
    }


def load_tag_overrides(path: Path) -> dict:
    data = parse_simple_yaml(path)

    def section(name: str) -> dict:
        sec = data.get(name)
        return sec if isinstance(sec, dict) else {}

    out = {
        "module_math_tags": section("module_math_tags"),
        "module_applied_tags": section("module_applied_tags"),
        "module_profiles": section("module_profiles"),
        "decl_math_tags": section("decl_math_tags"),
        "decl_applied_tags": section("decl_applied_tags"),
        "decl_profiles": section("decl_profiles"),
        "concept_math_tags": section("concept_math_tags"),
        "concept_applied_tags": section("concept_applied_tags"),
        "concept_profiles": section("concept_profiles"),
        "source": str(path),
    }
    return out


def fallback_profile_axis_tags(profile_id: str) -> tuple[list[str], list[str]]:
    math_map = {
        "learning": ["probability", "statistics", "analysis", "linear_algebra"],
        "probability": ["probability", "measure_theory"],
        "statistics": ["statistics", "probability", "measure_theory"],
        "optimization": ["analysis", "linear_algebra", "numerical"],
        "rl": ["probability", "measure_theory", "analysis", "linear_algebra"],
        "bandits": ["probability", "statistics", "analysis"],
        "ai": ["linear_algebra", "analysis", "probability"],
        "llm": ["linear_algebra", "analysis", "probability", "tensor_analysis"],
    }
    applied_map = {
        "learning": ["learning_theory", "statistics"],
        "probability": ["statistics"],
        "statistics": ["statistics", "information_theory"],
        "optimization": ["optimization", "online_learning"],
        "rl": ["reinforcement_learning", "control"],
        "bandits": ["bandits", "online_learning"],
        "ai": ["ai_applications", "learning_theory"],
        "llm": ["llm", "ai_applications"],
    }
    return math_map.get(profile_id, []), applied_map.get(profile_id, [])


def layer_from_module(module: str) -> str:
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module-graph", type=Path, required=True, help="module_graph.json path")
    ap.add_argument("--decl-graph", type=Path, required=True, help="decl_graph.json path")
    ap.add_argument("--usage-graph", type=Path, required=True, help="usage_graph.json path")
    ap.add_argument(
        "--retrieval-events",
        type=Path,
        default=Path("artifacts/telemetry/retrieval.jsonl"),
        help="retrieval telemetry jsonl path",
    )
    ap.add_argument("--modules", type=Path, required=True, help="modules.json path")
    ap.add_argument("--taxonomy", type=Path, required=True, help="docs/meta/taxonomy.yaml path")
    ap.add_argument("--canon", type=Path, required=True, help="docs/meta/canon.yaml path")
    ap.add_argument(
        "--domains",
        type=Path,
        default=Path("docs/meta/domains.yaml"),
        help="docs/meta/domains.yaml path",
    )
    ap.add_argument(
        "--taxonomy-math",
        type=Path,
        default=Path("docs/meta/taxonomy_math.yaml"),
        help="docs/meta/taxonomy_math.yaml path",
    )
    ap.add_argument(
        "--taxonomy-applied",
        type=Path,
        default=Path("docs/meta/taxonomy_applied.yaml"),
        help="docs/meta/taxonomy_applied.yaml path",
    )
    ap.add_argument(
        "--domain-profiles",
        type=Path,
        default=Path("docs/meta/domain_profiles.yaml"),
        help="docs/meta/domain_profiles.yaml path",
    )
    ap.add_argument(
        "--tags-overrides",
        type=Path,
        default=Path("docs/meta/tags_overrides.yaml"),
        help="docs/meta/tags_overrides.yaml path",
    )
    ap.add_argument(
        "--mathlib-slice",
        type=Path,
        default=Path("artifacts/index/mathlib_slice.json"),
        help="mathlib_slice.json path",
    )
    ap.add_argument(
        "--mathlib-imports",
        type=Path,
        default=Path("artifacts/index/mathlib_imports.json"),
        help="mathlib_imports.json path",
    )
    ap.add_argument(
        "--mathlib-hubs",
        type=Path,
        default=Path("artifacts/index/mathlib_hubs.json"),
        help="mathlib_hubs.json path",
    )
    ap.add_argument(
        "--mathlib-aggregators",
        type=Path,
        default=Path("artifacts/index/mathlib_aggregators.json"),
        help="mathlib_aggregators.json path",
    )
    ap.add_argument(
        "--mltheory-to-mathlib",
        type=Path,
        default=Path("artifacts/index/mltheory_to_mathlib.json"),
        help="mltheory_to_mathlib.json path",
    )
    ap.add_argument(
        "--max-mathlib-modules",
        type=int,
        default=220,
        help="max number of mathlib module nodes injected into subgraph",
    )
    ap.add_argument("--out", type=Path, required=True, help="subgraph.json output path")
    ap.add_argument(
        "--export-docs-data",
        type=Path,
        default=Path("docs/_auto/subgraph.json"),
        help="optional docs/_auto subgraph copy",
    )
    args = ap.parse_args()

    module_graph = load_json(args.module_graph.resolve())
    decl_graph = load_json(args.decl_graph.resolve())
    usage_graph = load_json(args.usage_graph.resolve())
    retrieval_events = load_jsonl(args.retrieval_events.resolve())
    modules = load_json(args.modules.resolve())
    taxonomy = parse_simple_yaml(args.taxonomy.resolve())
    canon_modules, canon_decls = load_canon(args.canon.resolve())
    domain_meta_legacy = load_domain_profiles_legacy(args.domains.resolve())
    math_axis_meta = load_axis_taxonomy(args.taxonomy_math.resolve(), "math")
    applied_axis_meta = load_axis_taxonomy(args.taxonomy_applied.resolve(), "applied")
    profile_axes_meta = load_profile_axes(args.domain_profiles.resolve())
    tag_overrides = load_tag_overrides(args.tags_overrides.resolve())

    legacy_profiles: dict[str, dict] = domain_meta_legacy["profiles"]
    axis_profiles: dict[str, dict] = profile_axes_meta["profiles"]
    domain_profiles: dict[str, dict] = {}
    profile_ids = sorted(set(legacy_profiles.keys()) | set(axis_profiles.keys()))
    for profile_id in profile_ids:
        legacy = legacy_profiles.get(profile_id, {})
        axis_row = axis_profiles.get(profile_id, {})
        fallback_math, fallback_applied = fallback_profile_axis_tags(profile_id)
        math_tags = as_str_list(axis_row.get("math_tags")) or fallback_math
        applied_tags = as_str_list(axis_row.get("applied_tags")) or fallback_applied
        domain_profiles[profile_id] = {
            "id": profile_id,
            "title": axis_row.get("title")
            if isinstance(axis_row.get("title"), str) and axis_row.get("title")
            else (
                legacy.get("title")
                if isinstance(legacy.get("title"), str) and legacy.get("title")
                else profile_id
            ),
            "description": axis_row.get("description")
            if isinstance(axis_row.get("description"), str)
            else (legacy.get("description") if isinstance(legacy.get("description"), str) else ""),
            "module_roots": as_str_list(legacy.get("module_roots")),
            "allowed_local_roots": as_str_list(legacy.get("allowed_local_roots")),
            "concept_binds": as_str_list(legacy.get("concept_binds")),
            "default_imports": as_str_list(legacy.get("default_imports")),
            "mathlib_slice_roots": as_str_list(legacy.get("mathlib_slice_roots")),
            "skills_whitelist": as_str_list(legacy.get("skills_whitelist")),
            "bridge_modules": as_str_list(legacy.get("bridge_modules")),
            "adjacent_domains": as_str_list(legacy.get("adjacent_domains")),
            "math_tags": math_tags,
            "applied_tags": applied_tags,
            "adjacent_profiles": as_str_list(axis_row.get("adjacent_profiles"))
            or as_str_list(legacy.get("adjacent_domains")),
        }

    default_profile = profile_axes_meta.get("default_profile")
    if not isinstance(default_profile, str) or default_profile not in domain_profiles:
        default_profile = domain_meta_legacy.get("default_domain")
    if not isinstance(default_profile, str) or default_profile not in domain_profiles:
        default_profile = "all"

    def load_optional(path: Path) -> dict:
        p = path.resolve()
        if not p.exists():
            return {}
        try:
            data = load_json(p)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

    mathlib_slice = load_optional(args.mathlib_slice)
    mathlib_imports = load_optional(args.mathlib_imports)
    mathlib_hubs = load_optional(args.mathlib_hubs)
    mathlib_aggregators = load_optional(args.mathlib_aggregators)
    mltheory_to_mathlib = load_optional(args.mltheory_to_mathlib)

    module_to_path = {}
    module_to_layer = {}
    for row in modules.get("modules", []):
        if not isinstance(row, dict):
            continue
        module = row.get("module")
        if not isinstance(module, str):
            continue
        module_to_path[module] = row.get("path", "")
        module_to_layer[module] = row.get("layer", layer_from_module(module))

    usage_top = {
        n.get("id")
        for n in usage_graph.get("nodes", [])[:80]
        if isinstance(n, dict) and isinstance(n.get("id"), str)
    }

    usage_stats_by_id: dict[str, dict] = {}
    for row in usage_graph.get("nodes", []):
        if not isinstance(row, dict):
            continue
        node_id = row.get("id")
        if not isinstance(node_id, str) or not node_id:
            continue
        usage_stats_by_id[node_id] = {
            "usage_count": int(row.get("usage_count", 0) or 0),
            "usage_success_count": int(row.get("success_count", 0) or 0),
            "usage_last_used": row.get("last_used", "") if isinstance(row.get("last_used"), str) else "",
        }

    retrieval_stats_by_id: dict[str, dict] = {}
    retrieval_recent_queries: list[dict] = []
    for event in retrieval_events:
        if not isinstance(event, dict):
            continue
        ts = event.get("timestamp", "")
        query = event.get("query", "")
        domain = event.get("domain", "")
        if isinstance(query, str) and query:
            retrieval_recent_queries.append(
                {
                    "timestamp": ts if isinstance(ts, str) else "",
                    "query": query,
                    "domain": domain if isinstance(domain, str) else "",
                    "duration_ms": float(event.get("duration_ms", 0.0) or 0.0),
                }
            )

        candidates = event.get("candidates", [])
        if isinstance(candidates, list):
            for cand in candidates:
                if not isinstance(cand, dict):
                    continue
                node_id = cand.get("id")
                if not isinstance(node_id, str) or not node_id:
                    continue
                row = retrieval_stats_by_id.setdefault(
                    node_id,
                    {
                        "retrieval_hit_count": 0,
                        "retrieval_final_hit_count": 0,
                        "retrieval_last_query": "",
                        "retrieval_last_stage": "",
                        "retrieval_last_source": "",
                        "retrieval_last_seen": "",
                    },
                )
                row["retrieval_hit_count"] += 1
                stage_name = cand.get("stage_name", "")
                source_name = cand.get("source", "")
                if isinstance(ts, str) and ts and ts >= row["retrieval_last_seen"]:
                    row["retrieval_last_seen"] = ts
                    row["retrieval_last_query"] = query if isinstance(query, str) else ""
                    row["retrieval_last_stage"] = stage_name if isinstance(stage_name, str) else ""
                    row["retrieval_last_source"] = source_name if isinstance(source_name, str) else ""

        final_hits = event.get("final_hits", [])
        if isinstance(final_hits, list):
            for node_id in final_hits:
                if not isinstance(node_id, str) or not node_id:
                    continue
                row = retrieval_stats_by_id.setdefault(
                    node_id,
                    {
                        "retrieval_hit_count": 0,
                        "retrieval_final_hit_count": 0,
                        "retrieval_last_query": "",
                        "retrieval_last_stage": "",
                        "retrieval_last_source": "",
                        "retrieval_last_seen": "",
                    },
                )
                row["retrieval_final_hit_count"] += 1
                if isinstance(ts, str) and ts and ts >= row["retrieval_last_seen"]:
                    row["retrieval_last_seen"] = ts
                    row["retrieval_last_query"] = query if isinstance(query, str) else ""
                    row["retrieval_last_stage"] = "final_hit"
                    row["retrieval_last_source"] = "retrieval.query"

    decl_to_module: dict[str, str] = {}
    for row in decl_graph.get("nodes", []):
        if not isinstance(row, dict):
            continue
        decl_id = row.get("name")
        module_id = row.get("module")
        if isinstance(decl_id, str) and decl_id and isinstance(module_id, str) and module_id:
            decl_to_module[decl_id] = module_id

    def usage_row_default() -> dict:
        return {
            "usage_count": 0,
            "usage_success_count": 0,
            "usage_last_used": "",
        }

    for decl_id, src in list(usage_stats_by_id.items()):
        module_id = decl_to_module.get(decl_id, "")
        if not module_id:
            continue
        dst = usage_stats_by_id.setdefault(module_id, usage_row_default())
        dst["usage_count"] += int(src.get("usage_count", 0) or 0)
        dst["usage_success_count"] += int(src.get("usage_success_count", 0) or 0)
        src_last = src.get("usage_last_used", "")
        if isinstance(src_last, str) and src_last and src_last >= dst.get("usage_last_used", ""):
            dst["usage_last_used"] = src_last

    def retrieval_row_default() -> dict:
        return {
            "retrieval_hit_count": 0,
            "retrieval_final_hit_count": 0,
            "retrieval_last_query": "",
            "retrieval_last_stage": "",
            "retrieval_last_source": "",
            "retrieval_last_seen": "",
        }

    for decl_id, src in list(retrieval_stats_by_id.items()):
        module_id = decl_to_module.get(decl_id, "")
        if not module_id:
            continue
        dst = retrieval_stats_by_id.setdefault(module_id, retrieval_row_default())
        dst["retrieval_hit_count"] += int(src.get("retrieval_hit_count", 0) or 0)
        dst["retrieval_final_hit_count"] += int(src.get("retrieval_final_hit_count", 0) or 0)
        src_last_seen = src.get("retrieval_last_seen", "")
        if (
            isinstance(src_last_seen, str)
            and src_last_seen
            and src_last_seen >= dst.get("retrieval_last_seen", "")
        ):
            dst["retrieval_last_seen"] = src_last_seen
            dst["retrieval_last_query"] = (
                src.get("retrieval_last_query", "")
                if isinstance(src.get("retrieval_last_query", ""), str)
                else ""
            )
            dst["retrieval_last_stage"] = (
                src.get("retrieval_last_stage", "")
                if isinstance(src.get("retrieval_last_stage", ""), str)
                else ""
            )
            dst["retrieval_last_source"] = (
                src.get("retrieval_last_source", "")
                if isinstance(src.get("retrieval_last_source", ""), str)
                else ""
            )

    nodes: list[dict] = []
    seen_nodes: set[str] = set()
    module_node_ids: set[str] = set()

    for row in module_graph.get("nodes", []):
        if not isinstance(row, dict):
            continue
        module_id = row.get("id")
        if not isinstance(module_id, str):
            continue
        if module_id in seen_nodes:
            continue
        seen_nodes.add(module_id)
        module_node_ids.add(module_id)
        nodes.append(
            {
                "id": module_id,
                "kind": "module",
                "title": row.get("title", module_id),
                "layer": module_to_layer.get(module_id, row.get("layer", "other")),
                "spine": module_id in canon_modules,
                "path": module_to_path.get(module_id, ""),
                "package": "mathlib" if module_id.startswith("Mathlib.") else "MLTheory",
            }
        )

    max_mathlib = max(0, int(args.max_mathlib_modules))
    selected_mathlib: set[str] = set()
    roots = [m for m in mathlib_slice.get("root_direct_imports", []) if isinstance(m, str)]
    selected_mathlib.update(m for m in roots if m.startswith("Mathlib"))

    agg_modules = [
        r.get("module")
        for r in mathlib_aggregators.get("aggregators", [])
        if isinstance(r, dict) and isinstance(r.get("module"), str)
    ]
    hub_modules = [
        r.get("module")
        for r in mathlib_hubs.get("top_by_fan_in", []) + mathlib_hubs.get("top_by_fan_out", [])
        if isinstance(r, dict) and isinstance(r.get("module"), str)
    ]
    selected_mathlib.update(m for m in agg_modules[:80] if m.startswith("Mathlib"))
    selected_mathlib.update(m for m in hub_modules[:120] if m.startswith("Mathlib"))

    slice_modules = [m for m in mathlib_slice.get("slice", []) if isinstance(m, str)]
    slice_modules = [m for m in slice_modules if m.startswith("Mathlib")]
    for m in slice_modules:
        if len(selected_mathlib) >= max_mathlib:
            break
        selected_mathlib.add(m)

    agg_set = set(m for m in agg_modules if isinstance(m, str))
    root_set = set(roots)
    for module_id in sorted(selected_mathlib):
        if module_id in seen_nodes:
            continue
        seen_nodes.add(module_id)
        module_node_ids.add(module_id)
        nodes.append(
            {
                "id": module_id,
                "kind": "module",
                "title": module_id,
                "layer": "mathlib",
                "spine": module_id in agg_set or module_id in root_set,
                "path": "",
                "package": "mathlib",
            }
        )

    for row in decl_graph.get("nodes", []):
        if not isinstance(row, dict):
            continue
        name = row.get("name")
        module = row.get("module")
        node_kind = row.get("kind")
        decl_kind = row.get("decl_kind")
        generated = row.get("generated")
        if not isinstance(name, str) or not isinstance(module, str):
            continue
        if node_kind != "decl":
            raise ValueError(f"decl_graph node `{name}` must have kind='decl', got {node_kind!r}")
        if not isinstance(decl_kind, str) or not decl_kind:
            raise ValueError(f"decl_graph node `{name}` missing non-empty decl_kind")
        if not isinstance(generated, bool):
            raise ValueError(f"decl_graph node `{name}` missing boolean generated")
        if module not in module_node_ids:
            raise ValueError(f"decl_graph node `{name}` refers missing module node `{module}`")
        if name in seen_nodes:
            continue
        seen_nodes.add(name)
        decl_node = {
            "id": name,
            "kind": "decl",
            "title": name.split(".")[-1],
            "layer": module_to_layer.get(module, layer_from_module(module)),
            "spine": (module in canon_modules) or (name in canon_decls) or (name in usage_top),
            "module": module,
            "decl_kind": decl_kind,
            "generated": generated,
            "path": module_to_path.get(module, ""),
            "package": "mathlib" if name.startswith("Mathlib.") else "MLTheory",
        }
        generated_reason = row.get("generated_reason")
        if isinstance(generated_reason, str) and generated_reason:
            decl_node["generated_reason"] = generated_reason
        nodes.append(decl_node)

    concept_nodes = taxonomy.get("nodes", [])
    for row in concept_nodes:
        if not isinstance(row, dict):
            continue
        cid = row.get("id")
        title = row.get("title")
        if not isinstance(cid, str) or not isinstance(title, str):
            continue
        nid = f"concept:{cid}"
        if nid in seen_nodes:
            continue
        seen_nodes.add(nid)
        nodes.append(
            {
                "id": nid,
                "kind": "concept",
                "title": title,
                "spine": bool(row.get("default_collapsed", False)) is False,
                "package": "MLTheory",
            }
        )

    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            continue
        usage_row = usage_stats_by_id.get(node_id, {})
        node["usage_count"] = int(usage_row.get("usage_count", 0) or 0)
        node["usage_success_count"] = int(usage_row.get("usage_success_count", 0) or 0)
        node["usage_last_used"] = (
            usage_row.get("usage_last_used", "")
            if isinstance(usage_row.get("usage_last_used", ""), str)
            else ""
        )

        retrieval_row = retrieval_stats_by_id.get(node_id, {})
        node["retrieval_hit_count"] = int(retrieval_row.get("retrieval_hit_count", 0) or 0)
        node["retrieval_final_hit_count"] = int(
            retrieval_row.get("retrieval_final_hit_count", 0) or 0
        )
        node["retrieval_last_query"] = (
            retrieval_row.get("retrieval_last_query", "")
            if isinstance(retrieval_row.get("retrieval_last_query", ""), str)
            else ""
        )
        node["retrieval_last_stage"] = (
            retrieval_row.get("retrieval_last_stage", "")
            if isinstance(retrieval_row.get("retrieval_last_stage", ""), str)
            else ""
        )
        node["retrieval_last_source"] = (
            retrieval_row.get("retrieval_last_source", "")
            if isinstance(retrieval_row.get("retrieval_last_source", ""), str)
            else ""
        )
        node["retrieval_last_seen"] = (
            retrieval_row.get("retrieval_last_seen", "")
            if isinstance(retrieval_row.get("retrieval_last_seen", ""), str)
            else ""
        )

    edges: list[dict] = []
    seen_edges: set[tuple[str, str, str]] = set()
    node_kind_by_id: dict[str, str] = {
        n["id"]: n["kind"]
        for n in nodes
        if isinstance(n, dict) and isinstance(n.get("id"), str) and isinstance(n.get("kind"), str)
    }

    def add_edge(src: str, dst: str, etype: str, weight: float | None = None):
        if src not in seen_nodes or dst not in seen_nodes:
            return
        key = (src, dst, etype)
        if key in seen_edges:
            return
        seen_edges.add(key)
        row = {"src": src, "dst": dst, "type": etype}
        if weight is not None:
            row["weight"] = float(weight)
        edges.append(row)

    for row in module_graph.get("edges", []):
        if not isinstance(row, dict):
            continue
        src = row.get("src")
        dst = row.get("dst")
        if isinstance(src, str) and isinstance(dst, str):
            add_edge(src, dst, "imports", row.get("weight"))

    module_ids_sorted = sorted(module_node_ids)
    module_id_set = set(module_ids_sorted)
    for child in module_ids_sorted:
        if "." not in child:
            continue
        parent = child.rsplit(".", 1)[0]
        while parent:
            if parent in module_id_set:
                add_edge(parent, child, "contains", 1.0)
                break
            if "." not in parent:
                break
            parent = parent.rsplit(".", 1)[0]

    for row in mathlib_imports.get("edges", []):
        if not isinstance(row, dict):
            continue
        src = row.get("src")
        dst = row.get("dst")
        if isinstance(src, str) and isinstance(dst, str):
            if src in selected_mathlib and dst in selected_mathlib:
                add_edge(src, dst, "imports", row.get("weight"))

    for row in decl_graph.get("edges", []):
        if not isinstance(row, dict):
            continue
        src = row.get("src")
        dst = row.get("dst")
        etype = row.get("type")
        if isinstance(src, str) and isinstance(dst, str) and isinstance(etype, str):
            add_edge(src, dst, etype)

    for row in decl_graph.get("nodes", []):
        if not isinstance(row, dict):
            continue
        name = row.get("name")
        module = row.get("module")
        if not isinstance(name, str) or not isinstance(module, str):
            continue
        if node_kind_by_id.get(name) != "decl":
            raise ValueError(f"decl_in_module src `{name}` must be decl")
        if node_kind_by_id.get(module) != "module":
            raise ValueError(f"decl_in_module dst `{module}` must be module")
        add_edge(name, module, "decl_in_module")

    for row in taxonomy.get("bindings", []):
        if not isinstance(row, dict):
            continue
        node = row.get("node")
        target = row.get("target")
        if not isinstance(node, str) or not isinstance(target, str):
            continue
        add_edge(f"concept:{node}", target, "binds")

    def module_matches_prefix(module_name: str, prefix: str) -> bool:
        return module_name == prefix or module_name.startswith(f"{prefix}.")

    def path_matches_prefix(path_name: str, prefix: str) -> bool:
        return path_name.startswith(prefix)

    def normalize_module_id(raw: str) -> str:
        return raw[:-5] if raw.endswith(".lean") else raw

    def collect_module_mathlib_imports() -> dict[str, list[str]]:
        out: dict[str, set[str]] = {}
        for row in module_graph.get("edges", []):
            if not isinstance(row, dict):
                continue
            if row.get("type") != "imports":
                continue
            src = row.get("src")
            dst = row.get("dst")
            if not isinstance(src, str) or not isinstance(dst, str):
                continue
            if not src.startswith("MLTheory."):
                continue
            if not dst.startswith("Mathlib."):
                continue
            out.setdefault(src, set()).add(dst)

        mapping = mltheory_to_mathlib.get("mapping") or mltheory_to_mathlib.get("module_mappings") or {}
        if isinstance(mapping, dict):
            for module_raw, row in mapping.items():
                if not isinstance(module_raw, str) or not isinstance(row, dict):
                    continue
                module_id = normalize_module_id(module_raw)
                if not module_id.startswith("MLTheory."):
                    continue
                direct = row.get("direct", [])
                if not isinstance(direct, list):
                    continue
                for dep in direct:
                    if isinstance(dep, str) and dep.startswith("Mathlib."):
                        out.setdefault(module_id, set()).add(dep)
        return {k: sorted(v) for k, v in out.items()}

    module_mathlib_imports = collect_module_mathlib_imports()
    math_axis_tags: dict[str, dict] = math_axis_meta.get("tags", {})
    applied_axis_tags: dict[str, dict] = applied_axis_meta.get("tags", {})
    override_lists = {
        key: {
            k: as_str_list(v)
            for k, v in sec.items()
            if isinstance(k, str) and k
        }
        for key, sec in tag_overrides.items()
        if isinstance(sec, dict)
    }

    def tag_matches_tag_spec(tag: dict, module_id: str, path_name: str, concept_tokens: set[str]) -> bool:
        if any(module_matches_prefix(module_id, root) for root in tag.get("module_roots", [])):
            return True
        if path_name and any(path_matches_prefix(path_name, root) for root in tag.get("path_roots", [])):
            return True
        binds = set(tag.get("concept_binds", []))
        if concept_tokens and binds and not concept_tokens.isdisjoint(binds):
            return True
        return False

    def math_tags_from_import_signature(module_id: str) -> list[str]:
        imports = module_mathlib_imports.get(module_id, [])
        if not imports:
            return []
        scored: list[tuple[str, int]] = []
        for tag_id, tag in math_axis_tags.items():
            roots = as_str_list(tag.get("mathlib_roots"))
            if not roots:
                continue
            hit = 0
            for dep in imports:
                if any(module_matches_prefix(dep, root) for root in roots):
                    hit += 1
            if hit > 0:
                scored.append((tag_id, hit))
        scored.sort(key=lambda x: (-x[1], x[0]))
        return [x[0] for x in scored[:3]]

    def profile_matches_axis_tags(profile: dict, math_tags: set[str], applied_tags: set[str]) -> bool:
        req_math = set(as_str_list(profile.get("math_tags")))
        req_applied = set(as_str_list(profile.get("applied_tags")))
        if req_math and req_math.isdisjoint(math_tags):
            return False
        if req_applied and req_applied.isdisjoint(applied_tags):
            return False
        if not req_math and not req_applied:
            return False
        return True

    module_profiles_by_id: dict[str, list[str]] = {}
    module_math_tags_by_id: dict[str, list[str]] = {}
    module_applied_tags_by_id: dict[str, list[str]] = {}
    for node in nodes:
        if not isinstance(node, dict) or node.get("kind") != "module":
            continue
        module_id = node.get("id")
        module_path = node.get("path", "")
        if not isinstance(module_id, str):
            continue
        if not isinstance(module_path, str):
            module_path = ""
        math_tags: set[str] = set()
        applied_tags: set[str] = set()

        for tag_id, tag in math_axis_tags.items():
            if tag_matches_tag_spec(tag, module_id, module_path, {module_id}):
                math_tags.add(tag_id)
        math_tags.update(math_tags_from_import_signature(module_id))

        for tag_id, tag in applied_axis_tags.items():
            if tag_matches_tag_spec(tag, module_id, module_path, {module_id}):
                applied_tags.add(tag_id)

        math_tags.update(override_lists.get("module_math_tags", {}).get(module_id, []))
        applied_tags.update(override_lists.get("module_applied_tags", {}).get(module_id, []))

        profiles: set[str] = set()
        for domain_id, profile in domain_profiles.items():
            if any(module_matches_prefix(module_id, root) for root in profile["module_roots"]):
                profiles.add(domain_id)
            if module_path and any(path_matches_prefix(module_path, root) for root in profile["allowed_local_roots"]):
                profiles.add(domain_id)
            if module_id in profile["concept_binds"]:
                profiles.add(domain_id)
            if profile_matches_axis_tags(profile, math_tags, applied_tags):
                profiles.add(domain_id)

        profiles.update(override_lists.get("module_profiles", {}).get(module_id, []))
        sorted_profiles = sorted(profiles)
        sorted_math_tags = sorted(math_tags)
        sorted_applied_tags = sorted(applied_tags)
        node["profiles"] = sorted_profiles
        node["domains"] = sorted_profiles
        node["math_tags"] = sorted_math_tags
        node["applied_tags"] = sorted_applied_tags
        module_profiles_by_id[module_id] = sorted_profiles
        module_math_tags_by_id[module_id] = sorted_math_tags
        module_applied_tags_by_id[module_id] = sorted_applied_tags

    for node in nodes:
        if not isinstance(node, dict) or node.get("kind") != "decl":
            continue
        decl_id = node.get("id")
        module_id = node.get("module")
        decl_path = node.get("path", "")
        if not isinstance(decl_id, str):
            continue
        if not isinstance(module_id, str):
            module_id = ""
        if not isinstance(decl_path, str):
            decl_path = ""
        math_tags: set[str] = set(module_math_tags_by_id.get(module_id, []))
        applied_tags: set[str] = set(module_applied_tags_by_id.get(module_id, []))
        for tag_id, tag in math_axis_tags.items():
            if tag_matches_tag_spec(tag, decl_id, decl_path, {decl_id}):
                math_tags.add(tag_id)
        for tag_id, tag in applied_axis_tags.items():
            if tag_matches_tag_spec(tag, decl_id, decl_path, {decl_id}):
                applied_tags.add(tag_id)
        math_tags.update(override_lists.get("decl_math_tags", {}).get(decl_id, []))
        applied_tags.update(override_lists.get("decl_applied_tags", {}).get(decl_id, []))

        profiles: set[str] = set(module_profiles_by_id.get(module_id, []))
        for domain_id, profile in domain_profiles.items():
            if any(module_matches_prefix(decl_id, root) for root in profile["module_roots"]):
                profiles.add(domain_id)
            if decl_path and any(path_matches_prefix(decl_path, root) for root in profile["allowed_local_roots"]):
                profiles.add(domain_id)
            if profile_matches_axis_tags(profile, math_tags, applied_tags):
                profiles.add(domain_id)
        profiles.update(override_lists.get("decl_profiles", {}).get(decl_id, []))
        node["profiles"] = sorted(profiles)
        node["domains"] = sorted(profiles)
        node["math_tags"] = sorted(math_tags)
        node["applied_tags"] = sorted(applied_tags)

    for node in nodes:
        if not isinstance(node, dict) or node.get("kind") != "concept":
            continue
        concept_id = node.get("id")
        if not isinstance(concept_id, str):
            continue
        concept_short = concept_id.removeprefix("concept:")
        math_tags: set[str] = set()
        applied_tags: set[str] = set()
        tokens = {concept_id, concept_short, f"concept:{concept_short}"}
        for tag_id, tag in math_axis_tags.items():
            binds = set(tag.get("concept_binds", []))
            if binds and not binds.isdisjoint(tokens):
                math_tags.add(tag_id)
        for tag_id, tag in applied_axis_tags.items():
            binds = set(tag.get("concept_binds", []))
            if binds and not binds.isdisjoint(tokens):
                applied_tags.add(tag_id)

        math_tags.update(override_lists.get("concept_math_tags", {}).get(concept_id, []))
        applied_tags.update(override_lists.get("concept_applied_tags", {}).get(concept_id, []))

        profiles: set[str] = set()
        for domain_id, profile in domain_profiles.items():
            binds = set(profile["concept_binds"])
            if concept_id in binds or concept_short in binds or f"concept:{concept_short}" in binds:
                profiles.add(domain_id)
            if profile_matches_axis_tags(profile, math_tags, applied_tags):
                profiles.add(domain_id)
        profiles.update(override_lists.get("concept_profiles", {}).get(concept_id, []))
        node["profiles"] = sorted(profiles)
        node["domains"] = sorted(profiles)
        node["math_tags"] = sorted(math_tags)
        node["applied_tags"] = sorted(applied_tags)

    for row in usage_graph.get("edges", []):
        if not isinstance(row, dict):
            continue
        src = row.get("src")
        dst = row.get("dst")
        w = row.get("weight", 1.0)
        if isinstance(src, str) and isinstance(dst, str):
            add_edge(src, dst, "used_recently", float(w))

    mapping = mltheory_to_mathlib.get("mapping") or mltheory_to_mathlib.get("module_mappings") or {}
    if isinstance(mapping, dict):
        for module_raw, row in mapping.items():
            if not isinstance(module_raw, str):
                continue
            module_id = normalize_module_id(module_raw)
            if module_id not in seen_nodes:
                continue
            if not isinstance(row, dict):
                continue
            direct = row.get("direct", [])
            if not isinstance(direct, list):
                continue
            for dep in direct:
                if isinstance(dep, str) and dep in seen_nodes:
                    add_edge(module_id, dep, "imports", 1.0)

    decl_in_module_targets: dict[str, set[str]] = {}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        if edge.get("type") != "decl_in_module":
            continue
        src = edge.get("src")
        dst = edge.get("dst")
        if isinstance(src, str) and isinstance(dst, str):
            decl_in_module_targets.setdefault(src, set()).add(dst)

    for node in nodes:
        if not isinstance(node, dict) or node.get("kind") != "decl":
            continue
        decl_id = node.get("id")
        decl_module = node.get("module")
        if not isinstance(decl_id, str) or not isinstance(decl_module, str):
            raise ValueError(f"decl node malformed: {node!r}")
        if node_kind_by_id.get(decl_module) != "module":
            raise ValueError(f"decl `{decl_id}` references non-module `{decl_module}`")
        if decl_module not in decl_in_module_targets.get(decl_id, set()):
            raise ValueError(
                f"decl `{decl_id}` missing decl_in_module edge to `{decl_module}`"
            )

    node_domains_by_id: dict[str, set[str]] = {}
    node_math_tags_by_id: dict[str, set[str]] = {}
    node_applied_tags_by_id: dict[str, set[str]] = {}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        raw_domains = node.get("domains", [])
        raw_math_tags = node.get("math_tags", [])
        raw_applied_tags = node.get("applied_tags", [])
        if not isinstance(node_id, str):
            continue
        domains = set(as_str_list(raw_domains))
        math_tags = set(as_str_list(raw_math_tags))
        applied_tags = set(as_str_list(raw_applied_tags))
        node["domains"] = sorted(domains)
        node["profiles"] = sorted(domains)
        node["math_tags"] = sorted(math_tags)
        node["applied_tags"] = sorted(applied_tags)
        node_domains_by_id[node_id] = domains
        node_math_tags_by_id[node_id] = math_tags
        node_applied_tags_by_id[node_id] = applied_tags

    for edge in edges:
        if not isinstance(edge, dict):
            continue
        src = edge.get("src")
        dst = edge.get("dst")
        if not isinstance(src, str) or not isinstance(dst, str):
            continue
        src_domains = node_domains_by_id.get(src, set())
        dst_domains = node_domains_by_id.get(dst, set())
        union_domains = sorted(src_domains | dst_domains)
        if union_domains:
            edge["domains"] = union_domains
        src_math = node_math_tags_by_id.get(src, set())
        dst_math = node_math_tags_by_id.get(dst, set())
        src_applied = node_applied_tags_by_id.get(src, set())
        dst_applied = node_applied_tags_by_id.get(dst, set())
        union_math = sorted(src_math | dst_math)
        union_applied = sorted(src_applied | dst_applied)
        if union_math:
            edge["math_tags"] = union_math
        if union_applied:
            edge["applied_tags"] = union_applied
        if src_domains and dst_domains and src_domains.isdisjoint(dst_domains):
            edge["cross_domain"] = True

    top_hubs_rows: list[dict] = []
    seen_hubs: set[str] = set()
    for row in mathlib_hubs.get("top_by_fan_in", []) + mathlib_hubs.get("top_by_fan_out", []):
        if not isinstance(row, dict):
            continue
        module = row.get("module")
        if not isinstance(module, str) or not module or module in seen_hubs:
            continue
        if module not in seen_nodes:
            continue
        seen_hubs.add(module)
        top_hubs_rows.append(
            {
                "module": module,
                "fan_in": int(row.get("fan_in", 0) or 0),
                "fan_out": int(row.get("fan_out", 0) or 0),
            }
        )
        if len(top_hubs_rows) >= 40:
            break

    aggregator_rows: list[dict] = []
    for row in mathlib_aggregators.get("aggregators", []):
        if not isinstance(row, dict):
            continue
        module = row.get("module")
        if not isinstance(module, str) or module not in seen_nodes:
            continue
        reasons = [str(x) for x in row.get("reason", []) if isinstance(x, str)]
        aggregator_rows.append(
            {
                "module": module,
                "fan_in": int(row.get("fan_in", 0) or 0),
                "fan_out": int(row.get("fan_out", 0) or 0),
                "reason": reasons,
            }
        )
        if len(aggregator_rows) >= 40:
            break

    usage_top_rows: list[dict] = []
    for node_id, row in usage_stats_by_id.items():
        if node_id not in seen_nodes:
            continue
        usage_count = int(row.get("usage_count", 0) or 0)
        if usage_count <= 0:
            continue
        usage_top_rows.append(
            {
                "id": node_id,
                "usage_count": usage_count,
                "usage_success_count": int(row.get("usage_success_count", 0) or 0),
                "usage_last_used": row.get("usage_last_used", "")
                if isinstance(row.get("usage_last_used", ""), str)
                else "",
            }
        )
    usage_top_rows.sort(
        key=lambda r: (-r["usage_count"], -r["usage_success_count"], r["id"])
    )

    retrieval_top_rows: list[dict] = []
    retrieval_final_rows: list[dict] = []
    for node_id, row in retrieval_stats_by_id.items():
        if node_id not in seen_nodes:
            continue
        hit_count = int(row.get("retrieval_hit_count", 0) or 0)
        final_hit_count = int(row.get("retrieval_final_hit_count", 0) or 0)
        if hit_count <= 0 and final_hit_count <= 0:
            continue
        entry = {
            "id": node_id,
            "retrieval_hit_count": hit_count,
            "retrieval_final_hit_count": final_hit_count,
            "retrieval_last_query": row.get("retrieval_last_query", "")
            if isinstance(row.get("retrieval_last_query", ""), str)
            else "",
            "retrieval_last_stage": row.get("retrieval_last_stage", "")
            if isinstance(row.get("retrieval_last_stage", ""), str)
            else "",
            "retrieval_last_source": row.get("retrieval_last_source", "")
            if isinstance(row.get("retrieval_last_source", ""), str)
            else "",
            "retrieval_last_seen": row.get("retrieval_last_seen", "")
            if isinstance(row.get("retrieval_last_seen", ""), str)
            else "",
        }
        if hit_count > 0:
            retrieval_top_rows.append(entry)
        if final_hit_count > 0:
            retrieval_final_rows.append(entry)

    retrieval_top_rows.sort(
        key=lambda r: (-r["retrieval_hit_count"], -r["retrieval_final_hit_count"], r["id"])
    )
    retrieval_final_rows.sort(
        key=lambda r: (-r["retrieval_final_hit_count"], -r["retrieval_hit_count"], r["id"])
    )

    retrieval_recent_queries.sort(
        key=lambda r: (
            r["timestamp"] if isinstance(r.get("timestamp"), str) else "",
            r["query"],
        ),
        reverse=True,
    )
    dedup_recent_queries: list[dict] = []
    seen_query_keys: set[tuple[str, str]] = set()
    for row in retrieval_recent_queries:
        query = row.get("query")
        domain = row.get("domain")
        if not isinstance(query, str) or not query:
            continue
        if not isinstance(domain, str):
            domain = ""
        key = (query, domain)
        if key in seen_query_keys:
            continue
        seen_query_keys.add(key)
        dedup_recent_queries.append(row)
        if len(dedup_recent_queries) >= 20:
            break

    payload = {
        "generated_at": str(date.today()),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "domains": {
            "version": 2,
            "default_domain": default_profile,
            "default_profile": default_profile,
            "source": str(args.domain_profiles.resolve()),
            "legacy_source": domain_meta_legacy["source"],
            "taxonomy_sources": {
                "math": math_axis_meta["source"],
                "applied": applied_axis_meta["source"],
                "overrides": tag_overrides["source"],
            },
            "profiles": [domain_profiles[k] for k in sorted(domain_profiles)],
            "axes": {
                "math": {
                    "default_tag": math_axis_meta["default_tag"],
                    "tags": [math_axis_tags[k] for k in sorted(math_axis_tags)],
                },
                "applied": {
                    "default_tag": applied_axis_meta["default_tag"],
                    "tags": [applied_axis_tags[k] for k in sorted(applied_axis_tags)],
                },
            },
        },
        "mathlib_lens": {
            "slice_roots": [m for m in roots if isinstance(m, str) and m in seen_nodes],
            "top_hubs": top_hubs_rows,
            "aggregators": aggregator_rows,
        },
        "usage": {
            "event_count": int(usage_graph.get("event_count", 0) or 0),
            "top_used": usage_top_rows[:24],
        },
        "retrieval": {
            "event_count": len(retrieval_events),
            "top_hits": retrieval_top_rows[:24],
            "top_final_hits": retrieval_final_rows[:24],
            "recent_queries": dedup_recent_queries,
        },
        "nodes": sorted(nodes, key=lambda n: (n["kind"], n["id"])),
        "edges": sorted(edges, key=lambda e: (e["type"], e["src"], e["dst"])),
    }

    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    export_path = args.export_docs_data.resolve()
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"[gen_subgraph] wrote {out} and {export_path} "
        f"({len(nodes)} nodes / {len(edges)} edges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
