#!/usr/bin/env python3
"""Validate meta/index/graph artifact contracts for vNext workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


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
            s = line.strip()
            if indent == 0 and s.endswith(":"):
                if section in {"nodes", "bindings"} and current is not None:
                    result.setdefault(section, []).append(current)
                    current = None
                section = s[:-1]
                if section not in result:
                    result[section] = [] if section in {"nodes", "bindings", "canonical_modules", "canonical_decls"} else {}
                continue
            if section in {"nodes", "bindings"}:
                if s.startswith("- "):
                    if current is not None:
                        result[section].append(current)
                    current = {}
                    tail = s[2:].strip()
                    if ":" in tail:
                        k, v = tail.split(":", 1)
                        current[k.strip()] = v.strip().strip('"').strip("'")
                    continue
                if current is not None and ":" in s:
                    k, v = s.split(":", 1)
                    current[k.strip()] = v.strip().strip('"').strip("'")
                continue
            if section in {"canonical_modules", "canonical_decls"} and s.startswith("- "):
                result[section].append(s[2:].strip().strip('"').strip("'"))
                continue

            if section is not None and isinstance(result.get(section), dict):
                if ":" in s:
                    k, v = s.split(":", 1)
                    key = k.strip()
                    val = v.strip()
                    if val == "":
                        result[section][key] = []
                    else:
                        result[section][key] = val.strip('"').strip("'")
                elif s.startswith("- "):
                    keys = list(result[section].keys())
                    if keys:
                        result[section][keys[-1]].append(s[2:].strip().strip('"').strip("'"))
    if section in {"nodes", "bindings"} and current is not None:
        result.setdefault(section, []).append(current)
    return result


def load_json(path: Path, errors: list[str]) -> dict | None:
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(ROOT)}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            errors.append(f"{path.relative_to(ROOT)}: root must be object")
            return None
        return data
    except json.JSONDecodeError as err:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {err}")
        return None


def require_keys(obj: dict, keys: list[str], label: str, errors: list[str]) -> None:
    for key in keys:
        if key not in obj:
            errors.append(f"{label}: missing key `{key}`")


def as_str_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [x for x in value if isinstance(x, str) and x]


def validate_meta(errors: list[str]) -> None:
    taxonomy = parse_simple_yaml(ROOT / "docs" / "meta" / "taxonomy.yaml")
    aliases = parse_simple_yaml(ROOT / "docs" / "meta" / "aliases.yaml")
    canon = parse_simple_yaml(ROOT / "docs" / "meta" / "canon.yaml")

    nodes = taxonomy.get("nodes", [])
    if not isinstance(nodes, list) or not nodes:
        errors.append("docs/meta/taxonomy.yaml: `nodes` must be non-empty list")
    else:
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                errors.append(f"taxonomy.nodes[{i}] must be object")
                continue
            if not node.get("id") or not node.get("title"):
                errors.append(f"taxonomy.nodes[{i}] missing id/title")

    aliases_map = aliases.get("aliases")
    if not isinstance(aliases_map, dict):
        errors.append("docs/meta/aliases.yaml: missing mapping `aliases`")

    canon_mods = canon.get("canonical_modules")
    if not isinstance(canon_mods, list):
        errors.append("docs/meta/canon.yaml: `canonical_modules` must be list")

    domains_path = ROOT / "docs" / "meta" / "domains.yaml"
    if domains_path.exists():
        domains = parse_simple_yaml(domains_path)
        module_roots = domains.get("domain_module_roots")
        local_roots = domains.get("domain_allowed_local_roots")
        concept_binds = domains.get("domain_concept_binds")
        if not isinstance(module_roots, dict) or not module_roots:
            errors.append("docs/meta/domains.yaml: `domain_module_roots` must be non-empty mapping")
        if not isinstance(local_roots, dict) or not local_roots:
            errors.append("docs/meta/domains.yaml: `domain_allowed_local_roots` must be non-empty mapping")
        if concept_binds is not None and not isinstance(concept_binds, dict):
            errors.append("docs/meta/domains.yaml: `domain_concept_binds` must be mapping when present")

        domain_ids: set[str] = set()
        if isinstance(module_roots, dict):
            domain_ids.update(k for k in module_roots if isinstance(k, str) and k)
        if isinstance(local_roots, dict):
            domain_ids.update(k for k in local_roots if isinstance(k, str) and k)
        if not domain_ids:
            errors.append("docs/meta/domains.yaml: no domain ids found")
        for domain_id in sorted(domain_ids):
            roots = as_str_list(module_roots.get(domain_id)) if isinstance(module_roots, dict) else []
            allowed = as_str_list(local_roots.get(domain_id)) if isinstance(local_roots, dict) else []
            if not roots:
                errors.append(f"docs/meta/domains.yaml: domain `{domain_id}` missing module_roots")
            if not allowed:
                errors.append(f"docs/meta/domains.yaml: domain `{domain_id}` missing allowed_local_roots")

    for extra_meta in (
        ROOT / "docs" / "meta" / "taxonomy_math.yaml",
        ROOT / "docs" / "meta" / "taxonomy_applied.yaml",
        ROOT / "docs" / "meta" / "domain_profiles.yaml",
    ):
        if not extra_meta.exists():
            continue
        cfg = parse_simple_yaml(extra_meta)
        titles = cfg.get("tag_titles") or cfg.get("profile_titles")
        if not isinstance(titles, dict) or not titles:
            errors.append(f"{extra_meta.relative_to(ROOT)}: expected non-empty tag/profile titles mapping")

    backlog_path = ROOT / "docs" / "meta" / "backlog.yaml"
    if backlog_path.exists():
        backlog = parse_simple_yaml(backlog_path)
        backlog_cfg = backlog.get("config")
        if isinstance(backlog_cfg, dict):
            default_state = backlog_cfg.get("default_state")
            allowed_states = backlog_cfg.get("allowed_states")
        else:
            default_state = backlog.get("default_state")
            allowed_states = backlog.get("allowed_states")
        if not isinstance(default_state, str) or not default_state:
            errors.append("docs/meta/backlog.yaml: `default_state` must be non-empty string")
        if not isinstance(allowed_states, list) or not all(
            isinstance(x, str) and x for x in allowed_states
        ):
            errors.append("docs/meta/backlog.yaml: `allowed_states` must be non-empty string list")
        elif isinstance(default_state, str) and default_state not in allowed_states:
            errors.append("docs/meta/backlog.yaml: `default_state` must be listed in `allowed_states`")

    ui_path = ROOT / "docs" / "meta" / "ui.yaml"
    if ui_path.exists():
        ui = parse_simple_yaml(ui_path)
        ui_defaults = ui.get("defaults")
        if isinstance(ui_defaults, dict):
            target = ui_defaults
        else:
            target = ui
        for key in (
            "default_scope",
            "default_spine_only",
            "default_expand_mode",
            "default_max_visible_nodes",
        ):
            value = target.get(key) if isinstance(target, dict) else None
            if value is None or value == "":
                errors.append(f"docs/meta/ui.yaml: `{key}` is required when file exists")


def validate_artifacts(errors: list[str]) -> None:
    domains_meta_exists = (ROOT / "docs" / "meta" / "domains.yaml").exists()
    modules = load_json(ROOT / "artifacts" / "index" / "modules.json", errors)
    imports = load_json(ROOT / "artifacts" / "index" / "imports.json", errors)
    decls = load_json(ROOT / "artifacts" / "index" / "decls.json", errors)
    module_graph = load_json(ROOT / "artifacts" / "graphs" / "module_graph.json", errors)
    decl_graph = load_json(ROOT / "artifacts" / "graphs" / "decl_graph.json", errors)
    subgraph = load_json(ROOT / "artifacts" / "graphs" / "subgraph.json", errors)
    usage_graph = load_json(ROOT / "artifacts" / "graphs" / "usage_graph.json", errors)
    usage_suggestions = load_json(ROOT / "artifacts" / "index" / "usage_suggestions.json", errors)
    decl_graph_decl_to_module: dict[str, str] = {}

    if modules is not None:
        require_keys(modules, ["generated_at", "modules"], "modules.json", errors)
        if not isinstance(modules.get("modules"), list):
            errors.append("modules.json: `modules` must be list")

    if imports is not None:
        require_keys(imports, ["generated_at", "nodes", "edges"], "imports.json", errors)
        if not isinstance(imports.get("edges"), list):
            errors.append("imports.json: `edges` must be list")

    if decls is not None:
        require_keys(decls, ["generated_at", "decls"], "decls.json", errors)
        if not isinstance(decls.get("decls"), list):
            errors.append("decls.json: `decls` must be list")

    if module_graph is not None:
        require_keys(module_graph, ["generated_at", "nodes", "edges"], "module_graph.json", errors)

    if decl_graph is not None:
        require_keys(decl_graph, ["nodes", "edges"], "decl_graph.json", errors)
        fallback_count = decl_graph.get("fallback_module_count")
        if fallback_count is not None and (not isinstance(fallback_count, int) or fallback_count < 0):
            errors.append("decl_graph.json: `fallback_module_count` must be a non-negative integer")
        if isinstance(fallback_count, int) and fallback_count >= 5:
            errors.append(
                f"decl_graph.json: `fallback_module_count` too large ({fallback_count}), expected < 5"
            )
        nodes = decl_graph.get("nodes", [])
        if not isinstance(nodes, list):
            errors.append("decl_graph.json: `nodes` must be list")
        else:
            for i, node in enumerate(nodes):
                if not isinstance(node, dict):
                    errors.append(f"decl_graph.json: nodes[{i}] must be object")
                    continue
                name = node.get("name")
                module = node.get("module")
                kind = node.get("kind")
                decl_kind = node.get("decl_kind")
                generated = node.get("generated")
                if not isinstance(name, str) or not name:
                    errors.append(f"decl_graph.json: nodes[{i}].name must be non-empty string")
                    continue
                if not isinstance(module, str) or not module:
                    errors.append(f"decl_graph.json: nodes[{i}] `{name}` missing non-empty module")
                if kind != "decl":
                    errors.append(f"decl_graph.json: nodes[{i}] `{name}` kind must be `decl`")
                if not isinstance(decl_kind, str) or not decl_kind:
                    errors.append(f"decl_graph.json: nodes[{i}] `{name}` missing non-empty decl_kind")
                if not isinstance(generated, bool):
                    errors.append(f"decl_graph.json: nodes[{i}] `{name}` missing boolean generated")
                if isinstance(module, str) and module:
                    decl_graph_decl_to_module[name] = module

    allowed_edge_types = {
        "imports",
        "contains",
        "decl_in_module",
        "uses_type",
        "uses_value",
        "binds",
        "alias_of",
        "used_recently",
    }
    if subgraph is not None:
        require_keys(subgraph, ["generated_at", "nodes", "edges"], "subgraph.json", errors)
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])
        if not isinstance(nodes, list):
            errors.append("subgraph.json: `nodes` must be list")
            nodes = []
        if not isinstance(edges, list):
            errors.append("subgraph.json: `edges` must be list")
            edges = []

        node_kind_by_id: dict[str, str] = {}
        decl_nodes: dict[str, str] = {}
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                errors.append(f"subgraph.json: nodes[{i}] must be object")
                continue
            nid = node.get("id")
            kind = node.get("kind")
            if not isinstance(nid, str) or not nid:
                errors.append(f"subgraph.json: nodes[{i}].id must be non-empty string")
                continue
            if not isinstance(kind, str) or not kind:
                errors.append(f"subgraph.json: nodes[{i}] `{nid}` missing kind")
                continue
            if nid in node_kind_by_id:
                errors.append(f"subgraph.json: duplicate node id `{nid}`")
            node_kind_by_id[nid] = kind
            domains = node.get("domains")
            if not isinstance(domains, list) or not all(isinstance(x, str) for x in domains):
                errors.append(f"subgraph.json: node `{nid}` missing string-list `domains`")
            profiles = node.get("profiles")
            if not isinstance(profiles, list) or not all(isinstance(x, str) for x in profiles):
                errors.append(f"subgraph.json: node `{nid}` missing string-list `profiles`")
            math_tags = node.get("math_tags")
            if not isinstance(math_tags, list) or not all(isinstance(x, str) for x in math_tags):
                errors.append(f"subgraph.json: node `{nid}` missing string-list `math_tags`")
            applied_tags = node.get("applied_tags")
            if not isinstance(applied_tags, list) or not all(isinstance(x, str) for x in applied_tags):
                errors.append(f"subgraph.json: node `{nid}` missing string-list `applied_tags`")
            if kind == "decl":
                module = node.get("module")
                generated = node.get("generated")
                if not isinstance(module, str) or not module:
                    errors.append(f"subgraph.json: decl node `{nid}` missing non-empty module")
                else:
                    decl_nodes[nid] = module
                if not isinstance(generated, bool):
                    errors.append(f"subgraph.json: decl node `{nid}` missing boolean generated")

        decl_in_module_edges: dict[str, set[str]] = {}
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                errors.append(f"subgraph.json: edges[{i}] must be object")
                continue
            etype = edge.get("type")
            if etype not in allowed_edge_types:
                errors.append(f"subgraph.json: edges[{i}].type invalid: {etype}")
                continue
            if etype == "decl_in_module":
                src = edge.get("src")
                dst = edge.get("dst")
                if not isinstance(src, str) or not isinstance(dst, str):
                    errors.append(f"subgraph.json: edges[{i}] decl_in_module must have string src/dst")
                    continue
                if node_kind_by_id.get(src) != "decl":
                    errors.append(f"subgraph.json: decl_in_module src `{src}` must be decl node")
                if node_kind_by_id.get(dst) != "module":
                    errors.append(f"subgraph.json: decl_in_module dst `{dst}` must be module node")
                decl_in_module_edges.setdefault(src, set()).add(dst)

        for decl_id, module in decl_nodes.items():
            if node_kind_by_id.get(module) != "module":
                errors.append(
                    f"subgraph.json: decl `{decl_id}` module `{module}` is missing or not a module node"
                )
            if module not in decl_in_module_edges.get(decl_id, set()):
                errors.append(
                    f"subgraph.json: decl `{decl_id}` missing decl_in_module edge to `{module}`"
                )
            expected_module = decl_graph_decl_to_module.get(decl_id)
            if expected_module is not None and expected_module != module:
                errors.append(
                    f"subgraph.json: decl `{decl_id}` module mismatch "
                    f"(decl_graph={expected_module}, subgraph={module})"
                )

        domains_obj = subgraph.get("domains")
        if domains_meta_exists:
            if not isinstance(domains_obj, dict):
                errors.append("subgraph.json: missing `domains` object while docs/meta/domains.yaml exists")
            else:
                profiles = domains_obj.get("profiles")
                default_domain = domains_obj.get("default_domain")
                if not isinstance(profiles, list) or not profiles:
                    errors.append("subgraph.json: `domains.profiles` must be non-empty list")
                else:
                    for i, profile in enumerate(profiles):
                        if not isinstance(profile, dict):
                            errors.append(f"subgraph.json: domains.profiles[{i}] must be object")
                            continue
                        pid = profile.get("id")
                        if not isinstance(pid, str) or not pid:
                            errors.append(f"subgraph.json: domains.profiles[{i}] missing id")
                            continue
                        for key in ("module_roots", "allowed_local_roots", "concept_binds"):
                            val = profile.get(key)
                            if not isinstance(val, list) or not all(isinstance(x, str) for x in val):
                                errors.append(
                                    f"subgraph.json: domains.profiles[{i}] `{key}` must be string list"
                                )
                if not isinstance(default_domain, str) or not default_domain:
                    errors.append("subgraph.json: domains.default_domain must be non-empty string")
                default_profile = domains_obj.get("default_profile")
                if default_profile is not None and (not isinstance(default_profile, str) or not default_profile):
                    errors.append("subgraph.json: domains.default_profile must be non-empty string when present")
                if domains_obj.get("version") == 2:
                    axes = domains_obj.get("axes")
                    if not isinstance(axes, dict):
                        errors.append("subgraph.json: domains.axes must be object for v2")
                    else:
                        for axis in ("math", "applied"):
                            row = axes.get(axis)
                            if not isinstance(row, dict):
                                errors.append(f"subgraph.json: domains.axes.{axis} must be object")
                                continue
                            tags = row.get("tags")
                            if not isinstance(tags, list):
                                errors.append(f"subgraph.json: domains.axes.{axis}.tags must be list")

    if usage_graph is not None:
        require_keys(usage_graph, ["generated_at", "nodes", "edges"], "usage_graph.json", errors)

    if usage_suggestions is not None:
        require_keys(
            usage_suggestions,
            ["generated_at", "spine_candidates", "entry_module_candidates"],
            "usage_suggestions.json",
            errors,
        )


def main() -> int:
    errors: list[str] = []
    validate_meta(errors)
    validate_artifacts(errors)
    if errors:
        print("[check_meta_index_graph_contract] failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("[check_meta_index_graph_contract] passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
