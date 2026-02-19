#!/usr/bin/env python3
"""Unified MLTheory retrieval entrypoint with progressive widening + telemetry."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


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
                keys = list(result[section].keys())
                if keys:
                    result[section][keys[-1]].append(val)

    if section in {"nodes", "bindings"} and current is not None:
        result.setdefault(section, []).append(current)
    return result


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def as_str_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [x for x in value if isinstance(x, str) and x]


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def module_matches_prefix(module_name: str, prefix: str) -> bool:
    return module_name == prefix or module_name.startswith(f"{prefix}.")


def path_matches_prefix(path_name: str, prefix: str) -> bool:
    return path_name.startswith(prefix)


def tokenize(text: str) -> list[str]:
    return [tok for tok in re.split(r"[^A-Za-z0-9_']+", text.lower()) if tok]


def score_symbol(query: str, symbol: str, module: str) -> float:
    q = query.strip().lower()
    if not q:
        return 0.0
    sid = symbol.lower()
    mod = module.lower()
    score = 0.0

    if q == sid:
        score += 240.0
    if sid.startswith(q):
        score += 140.0
    if f".{q}" in sid:
        score += 105.0
    elif q in sid:
        score += 78.0
    if q in mod:
        score += 16.0

    q_tokens = tokenize(q)
    if q_tokens:
        hay = f"{sid} {mod}"
        hit_count = sum(1 for tok in q_tokens if tok in hay)
        if hit_count == 0:
            return 0.0
        score += hit_count * 19.0
        if sid.split(".")[-1].startswith(q_tokens[0]):
            score += 14.0
    return score


def load_domain_profiles(path: Path) -> tuple[str, dict[str, dict]]:
    data = parse_simple_yaml(path)

    def section(name: str) -> dict:
        sec = data.get(name)
        return sec if isinstance(sec, dict) else {}

    titles = section("domain_titles")
    module_roots = section("domain_module_roots")
    allowed_local_roots = section("domain_allowed_local_roots")
    default_imports = section("domain_default_imports")
    mathlib_slice_roots = section("domain_mathlib_slice_roots")
    bridge_modules = section("domain_bridge_modules")
    adjacent_domains = section("domain_adjacent_domains")

    domain_ids: set[str] = set()
    for sec in (
        titles,
        module_roots,
        allowed_local_roots,
        default_imports,
        mathlib_slice_roots,
        bridge_modules,
        adjacent_domains,
    ):
        domain_ids.update(k for k in sec if isinstance(k, str) and k)

    profiles: dict[str, dict] = {}
    for domain_id in sorted(domain_ids):
        profiles[domain_id] = {
            "id": domain_id,
            "title": titles.get(domain_id, domain_id)
            if isinstance(titles.get(domain_id, domain_id), str)
            else domain_id,
            "module_roots": as_str_list(module_roots.get(domain_id)),
            "allowed_local_roots": as_str_list(allowed_local_roots.get(domain_id)),
            "default_imports": as_str_list(default_imports.get(domain_id)),
            "mathlib_slice_roots": as_str_list(mathlib_slice_roots.get(domain_id)),
            "bridge_modules": as_str_list(bridge_modules.get(domain_id)),
            "adjacent_domains": as_str_list(adjacent_domains.get(domain_id)),
        }

    default_domain = data.get("default_domain")
    if not isinstance(default_domain, str) or default_domain not in profiles:
        default_domain = "all"

    return default_domain, profiles


def load_aliases(path: Path) -> dict[str, list[str]]:
    data = parse_simple_yaml(path)
    aliases = data.get("aliases")
    if not isinstance(aliases, dict):
        return {}
    out: dict[str, list[str]] = {}
    for k, v in aliases.items():
        if not isinstance(k, str) or not k:
            continue
        if isinstance(v, str):
            out[k.lower()] = [v]
            continue
        out[k.lower()] = as_str_list(v)
    return out


def infer_active_domain(
    explicit_domain: str,
    context_module: str,
    query: str,
    default_domain: str,
    profiles: dict[str, dict],
) -> str:
    if explicit_domain and explicit_domain in profiles:
        return explicit_domain

    if context_module:
        for domain_id, profile in profiles.items():
            roots = profile.get("module_roots", [])
            if any(module_matches_prefix(context_module, root) for root in roots):
                return domain_id

    query_lc = query.lower()
    for domain_id, profile in profiles.items():
        title = profile.get("title", "")
        if isinstance(title, str):
            title_lc = title.lower().replace(" ", "")
            if domain_id in query_lc or (title_lc and title_lc in query_lc.replace(" ", "")):
                return domain_id
    return default_domain


def build_query_terms(query: str, aliases: dict[str, list[str]]) -> list[str]:
    query = query.strip()
    out: list[str] = []
    if query:
        out.append(query)
    q_lc = query.lower()
    for key, values in aliases.items():
        if key == q_lc or (key and key in q_lc):
            out.extend(values[:6])
    seen: set[str] = set()
    dedup: list[str] = []
    for term in out:
        clean = term.strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        dedup.append(clean)
    return dedup


def load_decl_rows(path: Path) -> list[dict]:
    data = load_json(path)
    rows = data.get("nodes", [])
    if not isinstance(rows, list):
        return []
    out: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = row.get("name")
        module = row.get("module")
        if not isinstance(name, str) or not isinstance(module, str):
            continue
        out.append(
            {
                "name": name,
                "module": module,
                "generated": bool(row.get("generated", False)),
                "decl_kind": row.get("decl_kind") if isinstance(row.get("decl_kind"), str) else "",
            }
        )
    return out


def load_modules(path: Path) -> dict[str, dict]:
    data = load_json(path)
    modules = data.get("modules", [])
    if not isinstance(modules, list):
        return {}
    out: dict[str, dict] = {}
    for row in modules:
        if not isinstance(row, dict):
            continue
        module = row.get("module")
        if not isinstance(module, str) or not module:
            continue
        out[module] = {
            "path": row.get("path") if isinstance(row.get("path"), str) else "",
            "layer": row.get("layer") if isinstance(row.get("layer"), str) else "",
            "imports": as_str_list(row.get("imports")),
        }
    return out


def load_mathlib_roots(path: Path) -> list[str]:
    data = load_json(path)
    roots = data.get("root_direct_imports")
    if isinstance(roots, list):
        return [r for r in roots if isinstance(r, str) and r]
    return []


def search_decl_index(
    query_terms: list[str],
    decl_rows: list[dict],
    module_to_meta: dict[str, dict],
    module_roots: list[str],
    allowed_local_roots: list[str],
    max_candidates: int,
) -> list[dict]:
    candidates: list[dict] = []
    for row in decl_rows:
        name = row["name"]
        module = row["module"]
        module_path = module_to_meta.get(module, {}).get("path", "")
        if module_roots and not any(module_matches_prefix(module, root) for root in module_roots):
            if allowed_local_roots and module_path:
                if not any(path_matches_prefix(module_path, root) for root in allowed_local_roots):
                    continue
            else:
                continue
        elif allowed_local_roots and module_path:
            if not any(path_matches_prefix(module_path, root) for root in allowed_local_roots):
                continue

        best_score = 0.0
        best_term = ""
        for term in query_terms:
            score = score_symbol(term, name, module)
            if score > best_score:
                best_score = score
                best_term = term
        if best_score <= 0:
            continue
        if row.get("generated") is True:
            best_score -= 5.0
        candidates.append(
            {
                "id": name,
                "module": module,
                "kind": "decl",
                "score": best_score,
                "source": "local_index",
                "evidence": f"matched term `{best_term}` in decl index",
            }
        )
    candidates.sort(key=lambda c: (-c["score"], c["id"]))
    return candidates[:max_candidates]


def search_rg_local(
    query_terms: list[str],
    repo_root: Path,
    search_roots: list[str],
    decl_name_set: set[str],
    max_candidates: int,
) -> list[dict]:
    if not shutil.which("rg"):
        return []

    scan_paths = []
    for raw in search_roots:
        p = repo_root / raw
        if p.exists():
            scan_paths.append(str(p))
    if not scan_paths:
        for fallback in ("MLTheory", "Incubator"):
            p = repo_root / fallback
            if p.exists():
                scan_paths.append(str(p))
    if not scan_paths:
        return []

    symbol_pat = re.compile(r"\b(?:MLTheory|Mathlib|Incubator)\.[A-Za-z0-9_']+(?:\.[A-Za-z0-9_']+)+\b")
    merged: dict[str, dict] = {}
    line_budget = max(40, max_candidates * 12)

    for term in query_terms[:4]:
        cmd = [
            "rg",
            "-n",
            "--no-heading",
            "--max-count",
            str(line_budget),
            "--glob",
            "*.lean",
            term,
            *scan_paths,
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=8,
            )
        except (subprocess.TimeoutExpired, OSError):
            continue
        if proc.returncode not in (0, 1):
            continue
        for line in proc.stdout.splitlines():
            m = re.match(r"^(.+?):(\d+):(.*)$", line)
            if not m:
                continue
            src_file = m.group(1)
            line_no = m.group(2)
            content = m.group(3)
            for symbol in set(symbol_pat.findall(content)):
                if symbol not in decl_name_set and not symbol.startswith("MLTheory."):
                    continue
                score = score_symbol(term, symbol, symbol.rsplit(".", 1)[0]) + 24.0
                prev = merged.get(symbol)
                if prev is None or score > prev["score"]:
                    merged[symbol] = {
                        "id": symbol,
                        "module": symbol.rsplit(".", 1)[0],
                        "kind": "decl",
                        "score": score,
                        "source": "rg_local",
                        "evidence": f"{Path(src_file).as_posix()}:{line_no}",
                    }
    rows = sorted(merged.values(), key=lambda c: (-c["score"], c["id"]))
    return rows[:max_candidates]


def fetch_loogle_hits(query: str, timeout_s: float, max_hits: int) -> list[dict]:
    if not query.strip():
        return []
    url = "https://loogle.lean-lang.org/json?q=" + urllib.parse.quote(query.strip())
    req = urllib.request.Request(url, headers={"User-Agent": "MLTheory-retrieval-query/1.0"})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
    data = json.loads(body)
    if isinstance(data, dict):
        hits = data.get("hits")
        if not isinstance(hits, list):
            return []
        raw_hits = hits
    elif isinstance(data, list):
        raw_hits = data
    else:
        return []

    out: list[dict] = []
    for row in raw_hits:
        if not isinstance(row, dict):
            continue
        name = row.get("name")
        module = row.get("module")
        if not isinstance(name, str) or not name:
            continue
        out.append(
            {
                "name": name,
                "module": module if isinstance(module, str) else "",
                "type": row.get("type") if isinstance(row.get("type"), str) else "",
            }
        )
        if len(out) >= max_hits:
            break
    return out


def search_loogle(
    query_terms: list[str],
    roots_filter: list[str],
    timeout_s: float,
    max_hits: int,
    max_candidates: int,
) -> tuple[list[dict], str]:
    merged: dict[str, dict] = {}
    any_success = False
    for term in query_terms[:3]:
        if not term.strip():
            continue
        try:
            hits = fetch_loogle_hits(term, timeout_s=timeout_s, max_hits=max_hits)
            any_success = True
        except Exception:
            continue
        for hit in hits:
            name = hit["name"]
            module = hit["module"]
            if roots_filter and module:
                if not any(module_matches_prefix(module, root) for root in roots_filter):
                    continue
            score = score_symbol(term, name, module) + 41.0
            if roots_filter:
                score += 12.0
            prev = merged.get(name)
            evidence = hit["type"][:160] if hit["type"] else "loogle hit"
            if prev is None or score > prev["score"]:
                merged[name] = {
                    "id": name,
                    "module": module,
                    "kind": "decl",
                    "score": score,
                    "source": "loogle_json",
                    "evidence": evidence,
                }
    if not any_success:
        return [], "loogle_unavailable"
    rows = sorted(merged.values(), key=lambda c: (-c["score"], c["id"]))
    return rows[:max_candidates], ""


def search_leanexplore(
    query_terms: list[str],
    endpoint: str,
    timeout_s: float,
    max_candidates: int,
) -> tuple[list[dict], str]:
    if not endpoint:
        return [], "leanexplore_endpoint_not_configured"

    merged: dict[str, dict] = {}
    any_success = False
    for term in query_terms[:2]:
        term = term.strip()
        if not term:
            continue
        if "{query}" in endpoint:
            url = endpoint.replace("{query}", urllib.parse.quote(term))
        else:
            sep = "&" if "?" in endpoint else "?"
            url = f"{endpoint}{sep}q={urllib.parse.quote(term)}"
        req = urllib.request.Request(url, headers={"User-Agent": "MLTheory-retrieval-query/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                body = resp.read().decode("utf-8")
            data = json.loads(body)
        except Exception:
            continue

        any_success = True
        if isinstance(data, dict):
            hits = data.get("hits")
            if not isinstance(hits, list):
                hits = data.get("results") if isinstance(data.get("results"), list) else []
        elif isinstance(data, list):
            hits = data
        else:
            hits = []

        for row in hits:
            if not isinstance(row, dict):
                continue
            name = row.get("name") or row.get("decl") or row.get("symbol")
            module = row.get("module") or row.get("namespace") or ""
            if not isinstance(name, str) or not name:
                continue
            if not isinstance(module, str):
                module = ""
            score = score_symbol(term, name, module) + 32.0
            prev = merged.get(name)
            evidence = str(row.get("score", "leanexplore"))[:140]
            if prev is None or score > prev["score"]:
                merged[name] = {
                    "id": name,
                    "module": module,
                    "kind": "decl",
                    "score": score,
                    "source": "leanexplore",
                    "evidence": evidence,
                }
    if not any_success:
        return [], "leanexplore_unavailable"
    rows = sorted(merged.values(), key=lambda c: (-c["score"], c["id"]))
    return rows[:max_candidates], ""


def merge_candidates(
    merged: dict[str, dict],
    rows: list[dict],
    stage: int,
    stage_name: str,
) -> None:
    for row in rows:
        cid = row["id"]
        prev = merged.get(cid)
        if prev is None:
            merged[cid] = {
                "id": cid,
                "module": row.get("module", ""),
                "kind": row.get("kind", "decl"),
                "stage": stage,
                "stage_name": stage_name,
                "source": row.get("source", ""),
                "score": float(row.get("score", 0.0)),
                "evidence": [row.get("evidence", "")] if row.get("evidence") else [],
                "sources": [row.get("source", "")] if row.get("source") else [],
            }
            continue

        prev["score"] = max(float(prev.get("score", 0.0)), float(row.get("score", 0.0)))
        if stage < int(prev.get("stage", stage)):
            prev["stage"] = stage
            prev["stage_name"] = stage_name
        if row.get("source") and row["source"] not in prev["sources"]:
            prev["sources"].append(row["source"])
        if row.get("evidence") and row["evidence"] not in prev["evidence"]:
            prev["evidence"].append(row["evidence"])
        if not prev.get("module") and row.get("module"):
            prev["module"] = row["module"]
        if row.get("source") == "local_index":
            prev["source"] = "local_index"


def lean_batch_verify(symbols: list[str], repo_root: Path, timeout_s: float) -> tuple[dict[str, bool], str]:
    if not symbols:
        return {}, ""
    if not shutil.which("lake"):
        return {s: False for s in symbols}, "lake_not_found"

    tmp_dir = repo_root / "artifacts" / "telemetry"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_file = tmp_dir / "_tmp_retrieval_verify.lean"

    lines = ["import MLTheory", "import Mathlib", ""]
    line_to_symbol: dict[int, str] = {}
    start_line = len(lines) + 1
    for i, symbol in enumerate(symbols):
        lines.append(f"#check {symbol}")
        line_to_symbol[start_line + i] = symbol

    tmp_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    cmd = ["lake", "env", "lean", str(tmp_file)]
    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_s,
        )
        output = f"{proc.stdout}\n{proc.stderr}"
    except subprocess.TimeoutExpired:
        try:
            tmp_file.unlink(missing_ok=True)
        except OSError:
            pass
        return {s: False for s in symbols}, "lean_check_timeout"
    except OSError:
        try:
            tmp_file.unlink(missing_ok=True)
        except OSError:
            pass
        return {s: False for s in symbols}, "lean_check_os_error"
    finally:
        try:
            tmp_file.unlink(missing_ok=True)
        except OSError:
            pass

    failed_lines: set[int] = set()
    abs_pat = re.compile(re.escape(str(tmp_file)) + r":(\d+):\d+:\s*error:")
    rel_pat = re.compile(r"_tmp_retrieval_verify\.lean:(\d+):\d+:\s*error:")
    for m in abs_pat.finditer(output):
        failed_lines.add(int(m.group(1)))
    for m in rel_pat.finditer(output):
        failed_lines.add(int(m.group(1)))

    if proc.returncode != 0 and not failed_lines:
        return {s: False for s in symbols}, "lean_check_failed_unparsed"

    verified: dict[str, bool] = {}
    for line_no, symbol in line_to_symbol.items():
        verified[symbol] = line_no not in failed_lines
    return verified, ""


def verify_candidates(
    candidates: list[dict],
    decl_name_set: set[str],
    repo_root: Path,
    no_lean_check: bool,
    lean_timeout_s: float,
    allow_unverified: bool,
) -> tuple[list[dict], str]:
    unresolved: list[str] = []
    by_id: dict[str, dict] = {}
    for row in candidates:
        row["verified"] = False
        row["verify_method"] = ""
        if row["id"] in decl_name_set:
            row["verified"] = True
            row["verify_method"] = "decl_index"
        else:
            unresolved.append(row["id"])
        by_id[row["id"]] = row

    verify_err = ""
    if unresolved and not no_lean_check:
        checked, verify_err = lean_batch_verify(sorted(set(unresolved)), repo_root, lean_timeout_s)
        for symbol, ok in checked.items():
            row = by_id.get(symbol)
            if row is None:
                continue
            if ok:
                row["verified"] = True
                row["verify_method"] = "lean_check"

    out: list[dict] = []
    for row in candidates:
        if row["verified"] or allow_unverified:
            if not row["verified"]:
                row["verify_method"] = "unverified"
            out.append(row)
    return out, verify_err


def append_jsonl(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def append_usage_event(
    usage_event_file: Path,
    final_hits: list[str],
    context_module: str,
    task: str,
    query: str,
    domain: str,
) -> None:
    if not final_hits:
        return
    event = {
        "timestamp": iso_utc_now(),
        "status": "success",
        "source": "retrieval.query",
        "module": context_module,
        "task": task,
        "used_decls": sorted(set(final_hits)),
        "note": f"query={query};domain={domain}",
    }
    append_jsonl(usage_event_file, event)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", type=str, required=True, help="goal keyword/query")
    ap.add_argument("--goal", type=str, default="", help="goal summary for telemetry")
    ap.add_argument("--domain", type=str, default="", help="active domain id")
    ap.add_argument("--context-module", type=str, default="", help="current Lean module")
    ap.add_argument("--task", type=str, default="", help="task card id")
    ap.add_argument("--final-hit", action="append", default=[], help="final chosen declaration")
    ap.add_argument(
        "--auto-final-hit-top",
        type=int,
        default=0,
        help="auto pick top-N verified candidates as final hits when --final-hit is empty",
    )
    ap.add_argument(
        "--min-candidates-before-stop",
        type=int,
        default=12,
        help="stop widening when this many merged candidates are collected",
    )
    ap.add_argument("--max-candidates-per-stage", type=int, default=40)
    ap.add_argument("--emit-limit", type=int, default=30)
    ap.add_argument("--loogle-timeout", type=float, default=6.0)
    ap.add_argument("--lean-timeout", type=float, default=12.0)
    ap.add_argument("--no-loogle", action="store_true")
    ap.add_argument("--no-leanexplore", action="store_true")
    ap.add_argument("--no-lean-check", action="store_true")
    ap.add_argument("--allow-unverified", action="store_true")
    ap.add_argument(
        "--event-file",
        type=Path,
        default=Path("artifacts/telemetry/retrieval.jsonl"),
        help="retrieval telemetry jsonl output",
    )
    ap.add_argument(
        "--usage-event-file",
        type=Path,
        default=Path("artifacts/telemetry/usage_events.jsonl"),
        help="usage telemetry jsonl output (for recent-used graph)",
    )
    ap.add_argument("--domains-yaml", type=Path, default=Path("docs/meta/domains.yaml"))
    ap.add_argument("--aliases-yaml", type=Path, default=Path("docs/meta/aliases.yaml"))
    ap.add_argument("--decl-graph", type=Path, default=Path("artifacts/graphs/decl_graph.json"))
    ap.add_argument("--modules-index", type=Path, default=Path("artifacts/index/modules.json"))
    ap.add_argument("--mathlib-slice", type=Path, default=Path("artifacts/index/mathlib_slice.json"))
    ap.add_argument("--out", type=Path, default=None, help="optional JSON output file")
    ap.add_argument("--compact", action="store_true", help="print compact JSON")
    args = ap.parse_args()

    t0 = perf_counter()
    repo_root = Path(__file__).resolve().parents[2]
    missing_artifacts: list[str] = []

    domains_yaml = resolve_path(repo_root, args.domains_yaml)
    aliases_yaml = resolve_path(repo_root, args.aliases_yaml)
    decl_graph_path = resolve_path(repo_root, args.decl_graph)
    modules_path = resolve_path(repo_root, args.modules_index)
    mathlib_slice_path = resolve_path(repo_root, args.mathlib_slice)
    event_file = resolve_path(repo_root, args.event_file)
    usage_event_file = resolve_path(repo_root, args.usage_event_file)

    if not domains_yaml.exists():
        missing_artifacts.append(str(domains_yaml.relative_to(repo_root)))
    if not decl_graph_path.exists():
        missing_artifacts.append(str(decl_graph_path.relative_to(repo_root)))
    if not modules_path.exists():
        missing_artifacts.append(str(modules_path.relative_to(repo_root)))

    default_domain, profiles = load_domain_profiles(domains_yaml)
    aliases = load_aliases(aliases_yaml)
    decl_rows = load_decl_rows(decl_graph_path)
    module_to_meta = load_modules(modules_path)
    decl_name_set = {row["name"] for row in decl_rows}
    mathlib_roots = load_mathlib_roots(mathlib_slice_path)

    active_domain = infer_active_domain(
        explicit_domain=args.domain.strip(),
        context_module=args.context_module.strip(),
        query=args.query,
        default_domain=default_domain,
        profiles=profiles,
    )
    profile = profiles.get(
        active_domain,
        {
            "module_roots": [],
            "allowed_local_roots": [],
            "mathlib_slice_roots": [],
            "bridge_modules": [],
            "adjacent_domains": [],
            "default_imports": [],
        },
    )
    query_terms = build_query_terms(args.query, aliases)
    if not query_terms:
        query_terms = [args.query]

    candidates_by_id: dict[str, dict] = {}
    stage_reports: list[dict] = []
    min_needed = max(1, int(args.min_candidates_before_stop))
    max_stage = max(1, int(args.max_candidates_per_stage))
    stop_widening = False

    def stage_report_template(stage: int, name: str) -> dict:
        return {
            "stage": stage,
            "name": name,
            "status": "skipped",
            "reason": "",
            "query_terms": query_terms[:6],
            "candidate_count": 0,
            "duration_ms": 0.0,
        }

    def run_stage(stage: int, name: str, fn):
        nonlocal stop_widening
        row = stage_report_template(stage, name)
        if stop_widening:
            row["status"] = "skipped"
            row["reason"] = f"enough candidates collected ({len(candidates_by_id)} >= {min_needed})"
            stage_reports.append(row)
            return
        s0 = perf_counter()
        try:
            rows, status_reason = fn()
            merge_candidates(candidates_by_id, rows, stage=stage, stage_name=name)
            row["status"] = "ok"
            row["candidate_count"] = len(rows)
            if status_reason:
                row["reason"] = status_reason
        except Exception as err:
            row["status"] = "error"
            row["reason"] = str(err)
        row["duration_ms"] = round((perf_counter() - s0) * 1000.0, 2)
        stage_reports.append(row)
        if len(candidates_by_id) >= min_needed:
            stop_widening = True

    active_module_roots = as_str_list(profile.get("module_roots"))
    active_local_roots = as_str_list(profile.get("allowed_local_roots"))
    active_mathlib_roots = as_str_list(profile.get("mathlib_slice_roots")) or mathlib_roots[:6]
    adjacent_ids = as_str_list(profile.get("adjacent_domains"))
    bridge_modules = as_str_list(profile.get("bridge_modules"))

    def stage1():
        rows = search_decl_index(
            query_terms=query_terms,
            decl_rows=decl_rows,
            module_to_meta=module_to_meta,
            module_roots=active_module_roots,
            allowed_local_roots=active_local_roots,
            max_candidates=max_stage,
        )
        rg_rows = search_rg_local(
            query_terms=query_terms,
            repo_root=repo_root,
            search_roots=active_local_roots,
            decl_name_set=decl_name_set,
            max_candidates=max_stage,
        )
        rows.extend(rg_rows)
        rows.sort(key=lambda c: (-c["score"], c["id"]))
        dedup: dict[str, dict] = {}
        for row in rows:
            prev = dedup.get(row["id"])
            if prev is None or row["score"] > prev["score"]:
                dedup[row["id"]] = row
        return list(dedup.values())[:max_stage], ""

    def stage2():
        if args.no_loogle:
            return [], "loogle_disabled_by_flag"
        return search_loogle(
            query_terms=query_terms,
            roots_filter=active_mathlib_roots,
            timeout_s=max(1.0, float(args.loogle_timeout)),
            max_hits=max(30, max_stage * 3),
            max_candidates=max_stage,
        )

    def stage3():
        adj_module_roots: list[str] = []
        adj_local_roots: list[str] = []
        for adj in adjacent_ids:
            p = profiles.get(adj)
            if not p:
                continue
            adj_module_roots.extend(as_str_list(p.get("module_roots")))
            adj_local_roots.extend(as_str_list(p.get("allowed_local_roots")))
        rows = search_decl_index(
            query_terms=query_terms,
            decl_rows=decl_rows,
            module_to_meta=module_to_meta,
            module_roots=sorted(set(adj_module_roots + bridge_modules)),
            allowed_local_roots=sorted(set(adj_local_roots)),
            max_candidates=max_stage,
        )
        for row in rows:
            if row["module"] in bridge_modules:
                row["score"] += 9.0
                row["evidence"] = f"{row['evidence']}; bridge_module"
        rg_rows = search_rg_local(
            query_terms=query_terms,
            repo_root=repo_root,
            search_roots=sorted(set(adj_local_roots)),
            decl_name_set=decl_name_set,
            max_candidates=max_stage,
        )
        rows.extend(rg_rows)
        rows.sort(key=lambda c: (-c["score"], c["id"]))
        dedup: dict[str, dict] = {}
        for row in rows:
            prev = dedup.get(row["id"])
            if prev is None or row["score"] > prev["score"]:
                dedup[row["id"]] = row
        return list(dedup.values())[:max_stage], ""

    def stage4():
        rows = search_decl_index(
            query_terms=query_terms,
            decl_rows=decl_rows,
            module_to_meta=module_to_meta,
            module_roots=[],
            allowed_local_roots=[],
            max_candidates=max_stage,
        )
        rows = [row for row in rows if row["id"].startswith("MLTheory.")]
        rg_rows = search_rg_local(
            query_terms=query_terms,
            repo_root=repo_root,
            search_roots=["MLTheory", "Incubator"],
            decl_name_set=decl_name_set,
            max_candidates=max_stage,
        )
        rows.extend([row for row in rg_rows if row["id"].startswith("MLTheory.")])
        rows.sort(key=lambda c: (-c["score"], c["id"]))
        dedup: dict[str, dict] = {}
        for row in rows:
            prev = dedup.get(row["id"])
            if prev is None or row["score"] > prev["score"]:
                dedup[row["id"]] = row
        return list(dedup.values())[:max_stage], ""

    def stage5():
        if args.no_loogle:
            return [], "loogle_disabled_by_flag"
        return search_loogle(
            query_terms=query_terms,
            roots_filter=[],
            timeout_s=max(1.0, float(args.loogle_timeout)),
            max_hits=max(40, max_stage * 4),
            max_candidates=max_stage,
        )

    def stage6():
        if args.no_leanexplore:
            return [], "leanexplore_disabled_by_flag"
        endpoint_url = os.environ.get("LEANEXPLORE_JSON_URL", "")
        return search_leanexplore(
            query_terms=query_terms,
            endpoint=endpoint_url,
            timeout_s=max(1.0, float(args.loogle_timeout)),
            max_candidates=max_stage,
        )

    run_stage(1, "domain_local", stage1)
    run_stage(2, "domain_slice", stage2)
    run_stage(3, "adjacent_domain", stage3)
    run_stage(4, "full_mltheory", stage4)
    run_stage(5, "full_mathlib", stage5)
    run_stage(6, "external_semantic", stage6)

    merged_rows = sorted(
        candidates_by_id.values(),
        key=lambda row: (int(row.get("stage", 9)), -float(row.get("score", 0.0)), row.get("id", "")),
    )
    verify_pool = merged_rows[: max(int(args.emit_limit) * 3, int(args.emit_limit))]
    verified_rows, verify_err = verify_candidates(
        verify_pool,
        decl_name_set=decl_name_set,
        repo_root=repo_root,
        no_lean_check=args.no_lean_check,
        lean_timeout_s=max(2.0, float(args.lean_timeout)),
        allow_unverified=args.allow_unverified,
    )
    if verify_err:
        missing_artifacts.append(f"verify:{verify_err}")

    verified_rows.sort(
        key=lambda row: (int(row.get("stage", 9)), -float(row.get("score", 0.0)), row.get("id", ""))
    )
    emit_limit = max(1, int(args.emit_limit))
    emitted = verified_rows[:emit_limit]
    verified_ids = {row["id"] for row in emitted if row.get("verified")}

    final_hits = [h.strip() for h in args.final_hit if isinstance(h, str) and h.strip()]
    if not final_hits and int(args.auto_final_hit_top) > 0:
        limit = max(1, int(args.auto_final_hit_top))
        final_hits = [row["id"] for row in emitted if row.get("verified")][:limit]

    final_hits = list(dict.fromkeys(final_hits))
    unresolved_final = [h for h in final_hits if h not in verified_ids]
    if unresolved_final and not args.no_lean_check:
        checked, _ = lean_batch_verify(
            symbols=unresolved_final,
            repo_root=repo_root,
            timeout_s=max(2.0, float(args.lean_timeout)),
        )
        final_hits = [h for h in final_hits if h in verified_ids or checked.get(h, False)]
    elif unresolved_final and not args.allow_unverified:
        final_hits = [h for h in final_hits if h in verified_ids]

    append_usage_event(
        usage_event_file=usage_event_file,
        final_hits=final_hits,
        context_module=args.context_module.strip(),
        task=args.task.strip(),
        query=args.query,
        domain=active_domain,
    )

    elapsed_ms = round((perf_counter() - t0) * 1000.0, 2)
    payload = {
        "generated_at": iso_utc_now(),
        "query": args.query,
        "goal": args.goal,
        "domain": active_domain,
        "artifact_mode": "fallback" if missing_artifacts else "full",
        "missing_artifacts": missing_artifacts,
        "widening_path": [
            row["name"] for row in stage_reports if row["status"] == "ok" and row["candidate_count"] > 0
        ],
        "stages": stage_reports,
        "candidates": [
            {
                "id": row["id"],
                "module": row.get("module", ""),
                "kind": row.get("kind", "decl"),
                "stage": int(row.get("stage", 0)),
                "stage_name": row.get("stage_name", ""),
                "source": row.get("source", ""),
                "score": round(float(row.get("score", 0.0)), 2),
                "verified": bool(row.get("verified", False)),
                "verify_method": row.get("verify_method", ""),
                "evidence": row.get("evidence", [])[:3],
            }
            for row in emitted
        ],
        "final_hits": final_hits,
        "duration_ms": elapsed_ms,
    }

    telemetry_event = {
        "timestamp": payload["generated_at"],
        "query": payload["query"],
        "goal": payload["goal"],
        "domain": payload["domain"],
        "artifact_mode": payload["artifact_mode"],
        "missing_artifacts": payload["missing_artifacts"],
        "widening_path": payload["widening_path"],
        "stages": payload["stages"],
        "candidates": payload["candidates"],
        "final_hits": payload["final_hits"],
        "duration_ms": payload["duration_ms"],
        "context_module": args.context_module,
        "task": args.task,
    }
    append_jsonl(event_file, telemetry_event)

    if args.out is not None:
        out_path = resolve_path(repo_root, args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=None if args.compact else 2) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(payload, ensure_ascii=False, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
