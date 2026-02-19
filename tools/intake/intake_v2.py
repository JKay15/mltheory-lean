#!/usr/bin/env python3
"""Intake v2 scaffolding for Research Pack -> Lean Commit in MLTheory."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path


RESEARCH_FILES = [
    "sources.md",
    "glossary.yaml",
    "outline.md",
    "candidate_lemmas.md",
    "gaps.md",
]

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "learning": (
        "learning", "generalization", "hypothesis", "classification", "regression",
        "risk", "sample", "pac", "kernel",
    ),
    "probability": (
        "probability", "measure", "random", "expectation", "variance", "martingale",
        "concentration", "tail", "distribution",
    ),
    "statistics": (
        "statistics", "statistical", "estimator", "likelihood", "inference",
        "hypothesis_test", "fisher", "kl", "bayes",
    ),
    "optimization": (
        "optimization", "convex", "gradient", "descent", "dual", "primal",
        "regret", "lagrangian",
    ),
    "rl": (
        "rl", "reinforcement", "mdp", "policy", "value", "q_learning", "bellman",
        "return", "td",
    ),
    "bandits": (
        "bandit", "arms", "ucb", "thompson", "exploration", "exploitation",
    ),
    "ai": (
        "ai", "agent", "planning", "decision", "reasoning", "search",
    ),
    "llm": (
        "llm", "language_model", "token", "transformer", "prompt", "alignment",
        "autoregressive",
    ),
}

PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD)\b|\?\?\?", flags=re.IGNORECASE)
SORRY_RE = re.compile(r"\bsorry\b")
AXIOM_RE = re.compile(r"^\s*axiom\b")
CACHE_PROMOTE_BEGIN_RE = re.compile(r"^\s*--\s*CACHE_PROMOTE_BEGIN\s*:?\s*([A-Za-z0-9_.-]+)\s*$")
CACHE_PROMOTE_END_RE = re.compile(r"^\s*--\s*CACHE_PROMOTE_END\s*:?\s*([A-Za-z0-9_.-]+)\s*$")


@dataclass
class DomainProfile:
    id: str
    module_roots: list[str]
    allowed_local_roots: list[str]
    concept_binds: list[str]
    default_imports: list[str]
    mathlib_slice_roots: list[str]
    skills_whitelist: list[str]
    bridge_modules: list[str]
    adjacent_domains: list[str]


@dataclass
class ProblemContext:
    repo_root: Path
    domain_tag: str
    domain_module: str
    problem: str
    problem_slug: str
    problem_title: str
    domains: list[str]
    domains_guess: list[str]
    domain_confidence: float
    domain_inference_mode: str

    @property
    def problem_dir(self) -> Path:
        return self.repo_root / "Incubator" / self.domain_module / self.problem

    @property
    def research_dir(self) -> Path:
        return self.problem_dir / "research"

    @property
    def namespace(self) -> str:
        return f"MLTheory.Incubator.{self.domain_module}.{self.problem}"

    @property
    def module_base(self) -> str:
        return f"Incubator.{self.domain_module}.{self.problem}"

    @property
    def spec_module(self) -> str:
        return f"{self.module_base}.Spec"

    @property
    def cache_module(self) -> str:
        return f"{self.module_base}.Cache"

    @property
    def sketch_module(self) -> str:
        return f"{self.module_base}.Sketch"

    @property
    def problem_id(self) -> str:
        return f"{self.domain_tag}.{self.problem_slug}"


@dataclass
class TaskCard:
    id: str
    title: str
    status: str
    blocker: str
    lean_target: str


@dataclass
class StuckBatchItem:
    lemma_id: str
    goal: str
    blocker: str
    attempts: list[tuple[str, str]]


@dataclass
class CachePromoteBlock:
    block_id: str
    content: str


def slug_to_module(raw: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", raw).strip("_")
    if not cleaned:
        raise ValueError(f"invalid empty identifier from `{raw}`")
    parts = [p for p in cleaned.split("_") if p]
    return "".join(p[:1].upper() + p[1:] for p in parts)


def slug_to_id(raw: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", raw).strip("_").lower()
    return cleaned or fallback


def normalize_batch_id(raw: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-")
    if not cleaned:
        raise ValueError(f"invalid empty batch id from `{raw}`")
    return cleaned


def parse_domains(raw: str | None, fallback_domain: str) -> list[str]:
    if raw is None or not raw.strip():
        return [fallback_domain.strip().lower()]
    items: list[str] = []
    seen: set[str] = set()
    for entry in raw.split(","):
        item = entry.strip().lower()
        if not item or item in seen:
            continue
        seen.add(item)
        items.append(item)
    return items or [fallback_domain.strip().lower()]


def tokenize_words(text: str) -> list[str]:
    raw = re.sub(r"[^A-Za-z0-9_]+", " ", text.lower())
    tokens = [t for t in raw.split() if t]
    expanded: list[str] = []
    for tok in tokens:
        expanded.append(tok)
        if "_" in tok:
            expanded.extend([part for part in tok.split("_") if part])
    return expanded


def infer_domains(
    *,
    domain_hint: str | None,
    explicit_domains_raw: str | None,
    default_domain: str,
    profiles: dict[str, DomainProfile],
    problem_slug: str,
    title: str,
    statement_text: str,
) -> tuple[list[str], list[str], float, str]:
    known_domains = set(profiles.keys())
    if not known_domains:
        raise RuntimeError("no domains loaded from docs/meta/domains.yaml")
    fallback = default_domain if default_domain in known_domains else sorted(known_domains)[0]

    if explicit_domains_raw and explicit_domains_raw.strip():
        domains = [d for d in parse_domains(explicit_domains_raw, fallback) if d in known_domains]
        if not domains:
            domains = [fallback]
        return domains, domains, 1.0, "manual"

    text = f"{problem_slug} {title} {statement_text}".strip()
    tokens = tokenize_words(text)
    token_set = set(tokens)
    score: dict[str, float] = {d: 0.0 for d in known_domains}

    for domain_id in known_domains:
        keywords = DOMAIN_KEYWORDS.get(domain_id, ())
        for kw in keywords:
            if kw in token_set:
                score[domain_id] += 1.0

    hint_norm = domain_hint.strip().lower() if isinstance(domain_hint, str) else ""
    if hint_norm in known_domains:
        score[hint_norm] += 1.5

    ranked = sorted(score.items(), key=lambda kv: (-kv[1], kv[0]))
    positives = [(d, s) for (d, s) in ranked if s > 0]

    if not positives:
        chosen = [hint_norm] if hint_norm in known_domains else [fallback]
        return chosen, chosen, 0.2, "fallback"

    total = sum(s for (_, s) in positives)
    top_domain, top_score = positives[0]
    chosen: list[str] = [top_domain]
    if len(positives) >= 2:
        second_domain, second_score = positives[1]
        if second_score >= top_score * 0.75:
            chosen.append(second_domain)
    guess = [d for (d, _) in positives[:3]]
    confidence = round(top_score / total, 3) if total > 0 else 0.2
    return chosen, guess, max(confidence, 0.2), "heuristic"


def as_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [x for x in value if isinstance(x, str) and x.strip()]


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
                    result[section] = [] if section in {"nodes", "bindings"} else {}
                continue

            if indent == 0 and ":" in s:
                if section in {"nodes", "bindings"} and current is not None:
                    result.setdefault(section, []).append(current)
                    current = None
                section = None
                k, v = s.split(":", 1)
                key = k.strip()
                val = v.strip()
                if val == "":
                    result[key] = []
                else:
                    result[key] = val.strip('"').strip("'")
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


def safe_yaml_scalar(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_.\-/ ]+", value):
        return value
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def safe_yaml_key(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_\- ]+", value):
        return value
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_if_missing(path: Path, content: str, *, force: bool = False) -> None:
    ensure_parent(path)
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")


def render_statement(ctx: ProblemContext) -> str:
    return f"""# Statement: {ctx.problem_title}\n\n- problem_id: `{ctx.problem_id}`\n- domains: {ctx.domains}\n- domains_guess: {ctx.domains_guess}\n- domain_confidence: `{ctx.domain_confidence}`\n- domain_inference_mode: `{ctx.domain_inference_mode}`\n- status: `research_pack_pending`\n- created_at: `{date.today()}`\n\n## Problem\n\nPaste the original problem statement here (paper/discussion/benchmark).\n\n## Acceptance\n\n- Complete the Research Pack (sources/glossary/outline/candidate_lemmas/gaps)\n- Produce compilable `Spec.lean` and task cards in Lean Commit stage\n\n## Domain Hint\n\n- primary_domain: `{ctx.domain_tag}`\n"""


def render_blueprint(ctx: ProblemContext) -> str:
    return f"""# Blueprint: {ctx.problem_title}\n\n- namespace: `{ctx.namespace}`\n- domains: {ctx.domains}\n\n## Planner Notes\n\n1. Fill proof skeleton (3-8 steps)\n2. Split intermediate lemmas\n3. Mark leaf tasks\n\n## Replan Batch Placeholder\n\n- stuck_batch_id: `batch-001`\n- blocked_lemmas: []\n- planner_actions: []\n"""


def render_sources_md(ctx: ProblemContext) -> str:
    return f"""# Sources\n\n> Each key fact must be traceable to a source.\n\n| fact_id | claim | source | location | confidence | notes |\n|---|---|---|---|---|---|\n| F1 | TODO | TODO | TODO | TODO | TODO |\n\nproblem_id: `{ctx.problem_id}`\n"""


def render_glossary_yaml(ctx: ProblemContext) -> str:
    return f"""version: 1\nproblem_id: {ctx.problem_id}\nterms:\n  - term: TODO\n    mltheory_symbol: TODO\n    mathlib_symbol: TODO\n    uncertainty: high\n"""


def render_outline_md(ctx: ProblemContext) -> str:
    return """# Outline\n\n1. TODO\n2. TODO\n3. TODO\n\n> Annotate the source of definitions/lemmas used in each step.\n"""


def render_candidate_lemmas_md(ctx: ProblemContext) -> str:
    return """# Candidate Lemmas\n\n| lemma_id | statement_nl | expected_symbol | source | certainty |\n|---|---|---|---|---|\n| L1 | TODO | TODO | TODO | low |\n"""


def render_gaps_md(ctx: ProblemContext) -> str:
    return """# Gaps\n\n| gap_id | kind | description | blocker_for | next_action |\n|---|---|---|---|---|\n| G1 | missing_lemma | TODO | L1 | TODO |\n"""


def render_spec_lean(ctx: ProblemContext) -> str:
    domain_label = ", ".join(ctx.domains)
    return f"""import MLTheory\n\nnamespace {ctx.namespace}\n\n/-- Intake v2 generated spec for {ctx.problem_title}.\nDomains: {domain_label}.\nThis declaration is intentionally minimal and compilable. -/\ndef ProblemSpec : Prop := True\n\nend {ctx.namespace}\n"""


def render_sketch_lean(ctx: ProblemContext) -> str:
    return f"""import MLTheory\n\nnamespace {ctx.namespace}\n\n/-- Incubator-only sketch metadata.\nUse this file for decomposition and temporary proof sketches.\nAvoid importing this file into Core/Methods modules. -/\ndef SketchPlan : List String := [\n  \"TODO: split target into 3-8 lemmas\",\n  \"TODO: mark leaf lemmas in Tasks.yaml\",\n  \"TODO: move proved lemmas into Cache.lean\"\n]\n\nend {ctx.namespace}\n"""


def render_cache_lean(ctx: ProblemContext) -> str:
    return f"""import MLTheory\n\nnamespace {ctx.namespace}\n\n/-- Cache file stores only proved lemmas for reuse. -/\ntheorem cache_bootstrap_true : True := by\n  trivial\n\nend {ctx.namespace}\n"""


def render_tasks_yaml(ctx: ProblemContext) -> str:
    title = json.dumps(ctx.problem_title, ensure_ascii=False)
    lines = [
        f"problem_id: {ctx.problem_id}",
        f"problem_title: {title}",
        "domains:",
    ]
    for d in ctx.domains:
        lines.append(f"  - {d}")
    lines.append("domains_guess:")
    for d in ctx.domains_guess:
        lines.append(f"  - {d}")
    lines.extend(
        [
            f"domain_confidence: {ctx.domain_confidence}",
            f"domain_inference_mode: {ctx.domain_inference_mode}",
            "status: spec_ready",
            "cards:",
            "  - id: L1",
            "    title: \"Lemma: TODO\"",
            "    depends_on: []",
            f"    lean_target: \"{ctx.namespace}.ProblemSpec\"",
            "    status: todo",
            "    blocker: \"\"",
        ]
    )
    return "\n".join(lines) + "\n"


def render_manifest(ctx: ProblemContext, phase: str) -> str:
    payload = {
        "version": 2,
        "problem_id": ctx.problem_id,
        "problem_title": ctx.problem_title,
        "domains": ctx.domains,
        "domains_guess": ctx.domains_guess,
        "domain_confidence": ctx.domain_confidence,
        "domain_inference_mode": ctx.domain_inference_mode,
        "namespace": ctx.namespace,
        "module_base": ctx.module_base,
        "phase": phase,
        "updated_at": str(date.today()),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def yaml_quote(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def render_stuck_batch_yaml(
    ctx: ProblemContext,
    batch_id: str,
    *,
    items: list[StuckBatchItem] | None = None,
) -> str:
    rows = items if items else [
        StuckBatchItem(
            lemma_id="L1",
            goal="TODO",
            blocker="TODO",
            attempts=[("simp?", "failed")],
        )
    ]
    lines = [
        f"batch_id: {batch_id}",
        f"problem_id: {ctx.problem_id}",
        "domains:",
    ]
    for d in ctx.domains:
        lines.append(f"  - {d}")
    lines.extend(
        [
            "status: open",
            "planner: GPTPro",
            "builder: Codex",
            "items:",
        ]
    )
    for row in rows:
        lemma_id = row.lemma_id.strip() or "L1"
        goal = row.goal.strip() or "TODO"
        blocker = row.blocker.strip() or "unspecified blocker"
        lines.append(f"  - lemma_id: {lemma_id}")
        lines.append(f"    goal: {yaml_quote(goal)}")
        lines.append("    attempts:")
        attempts = row.attempts if row.attempts else [("n/a", "failed")]
        for tactic, result in attempts:
            tactic_text = tactic.strip() or "n/a"
            result_text = result.strip() or "failed"
            lines.append(f"      - tactic: {yaml_quote(tactic_text)}")
            lines.append(f"        result: {yaml_quote(result_text)}")
        lines.append(f"    blocker: {yaml_quote(blocker)}")
    lines.extend(
        [
            "planner_reply:",
            "  split_into: []",
            "  hints: []",
            "  required_defs: []",
            "",
        ]
    )
    return "\n".join(lines)


def clean_yaml_scalar(raw: str) -> str:
    text = raw.strip()
    if not text:
        return ""
    if "#" in text:
        text = text.split("#", 1)[0].rstrip()
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    return text


def parse_inline_yaml_list(raw: str) -> list[str]:
    text = raw.strip()
    if not (text.startswith("[") and text.endswith("]")):
        return []
    inner = text[1:-1].strip()
    if not inner:
        return []
    out: list[str] = []
    for part in inner.split(","):
        item = clean_yaml_scalar(part)
        if item:
            out.append(item)
    return out


def parse_stuck_batch_file(path: Path) -> dict[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    split_into: list[str] = []
    hints: list[str] = []
    required_defs: list[str] = []
    item_lemma_ids: list[str] = []

    in_planner_reply = False
    active_list: str | None = None

    for raw in text.splitlines():
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "planner_reply:":
            in_planner_reply = True
            active_list = None
            continue
        if stripped == "items:":
            in_planner_reply = False
            active_list = None
            continue

        lemma_match = re.match(r"(?:-\s*)?lemma_id:\s*(.+)$", stripped)
        if lemma_match:
            lemma_id = clean_yaml_scalar(lemma_match.group(1))
            if lemma_id:
                item_lemma_ids.append(lemma_id)
            continue

        if not in_planner_reply:
            continue

        key_match = re.match(r"(split_into|hints|required_defs):\s*(.*)$", stripped)
        if key_match:
            active_list = key_match.group(1)
            tail = key_match.group(2).strip()
            if not tail:
                continue
            if tail == "[]":
                active_list = None
                continue
            values = parse_inline_yaml_list(tail)
            if active_list == "split_into":
                split_into.extend(values)
            elif active_list == "hints":
                hints.extend(values)
            elif active_list == "required_defs":
                required_defs.extend(values)
            active_list = None
            continue

        list_match = re.match(r"-\s*(.+)$", stripped)
        if list_match and active_list is not None:
            item = clean_yaml_scalar(list_match.group(1))
            if not item:
                continue
            if active_list == "split_into":
                split_into.append(item)
            elif active_list == "hints":
                hints.append(item)
            elif active_list == "required_defs":
                required_defs.append(item)

    return {
        "item_lemma_ids": item_lemma_ids,
        "split_into": split_into,
        "hints": hints,
        "required_defs": required_defs,
    }


def normalize_card_id(raw: str, fallback_index: int) -> str:
    base = raw.strip()
    if ":" in base:
        base = base.split(":", 1)[0].strip()
    if " " in base:
        base = base.split(" ", 1)[0].strip()
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", base).strip("_")
    if not cleaned:
        cleaned = f"L{fallback_index}"
    if cleaned[0].isdigit():
        cleaned = f"L_{cleaned}"
    return cleaned


def split_title(raw: str, fallback_id: str) -> str:
    text = raw.strip()
    if ":" in text:
        right = text.split(":", 1)[1].strip()
        if right:
            text = right
    text = text.replace('"', "'")
    if not text:
        text = fallback_id
    return text


def parse_existing_task_ids(tasks_text: str) -> set[str]:
    ids: set[str] = set()
    for raw in tasks_text.splitlines():
        m = re.match(r"^\s*-\s+id:\s*([A-Za-z0-9_.-]+)\s*$", raw)
        if m:
            ids.add(m.group(1))
    return ids


def parse_tasks_cards(path: Path) -> list[TaskCard]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    cards: list[TaskCard] = []
    in_cards = False
    current: dict[str, str] | None = None

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        card_id = current.get("id", "").strip()
        if card_id:
            cards.append(
                TaskCard(
                    id=card_id,
                    title=current.get("title", "").strip(),
                    status=current.get("status", "").strip().lower(),
                    blocker=current.get("blocker", "").strip(),
                    lean_target=current.get("lean_target", "").strip(),
                )
            )
        current = None

    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not in_cards:
            if stripped == "cards:":
                in_cards = True
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        if indent <= 1 and ":" in stripped and not stripped.startswith("- "):
            break

        id_match = re.match(r"^\s{2}-\s+id:\s*(.+)$", raw)
        if id_match:
            flush()
            current = {"id": clean_yaml_scalar(id_match.group(1))}
            continue

        field_match = re.match(r"^\s{4}([A-Za-z0-9_]+):\s*(.*)$", raw)
        if field_match and current is not None:
            key = field_match.group(1)
            val = clean_yaml_scalar(field_match.group(2))
            current[key] = val
    flush()
    return cards


def parse_failed_telemetry_attempts(path: Path) -> dict[str, list[tuple[str, str]]]:
    if not path.exists():
        return {}
    attempts: dict[str, list[tuple[str, str]]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        success = row.get("success")
        event = str(row.get("event", "")).strip()
        if success is True and "fail" not in event.lower():
            continue
        card_id = ""
        for key in ("card_id", "lemma_id", "task_id"):
            val = row.get(key)
            if isinstance(val, str) and val.strip():
                card_id = val.strip()
                break
        if not card_id:
            continue
        tactic = str(row.get("tactic", "n/a")).strip() or "n/a"
        reason = str(row.get("error", "")).strip() or str(row.get("result", "")).strip()
        if not reason:
            reason = event if event else "failed"
        attempts.setdefault(card_id, []).append((tactic, reason))
    return attempts


def nonempty_scalar(text: str) -> bool:
    value = clean_yaml_scalar(text).strip().lower()
    return value not in {"", "-", "none", "null"}


def collect_auto_stuck_items(ctx: ProblemContext, *, max_items: int) -> list[StuckBatchItem]:
    tasks_path = ctx.problem_dir / "Tasks.yaml"
    cards = parse_tasks_cards(tasks_path)
    telemetry = parse_failed_telemetry_attempts(ctx.problem_dir / "Telemetry.jsonl")

    items: list[StuckBatchItem] = []
    seen: set[str] = set()
    for card in cards:
        if card.id in seen:
            continue
        blocked = card.status in {"blocked", "stuck"} or nonempty_scalar(card.blocker)
        if not blocked:
            continue
        blocker = card.blocker if nonempty_scalar(card.blocker) else f"status={card.status or 'blocked'}"
        goal = card.lean_target or card.title or f"{ctx.namespace}.ProblemSpec"
        attempts = telemetry.get(card.id, [])
        if not attempts:
            attempts = [("n/a", blocker)]
        items.append(
            StuckBatchItem(
                lemma_id=card.id,
                goal=goal,
                blocker=blocker,
                attempts=attempts[:4],
            )
        )
        seen.add(card.id)
        if len(items) >= max_items:
            return items

    if items:
        return items

    for lemma_id, attempts in telemetry.items():
        lid = lemma_id.strip()
        if not lid or lid in seen:
            continue
        items.append(
            StuckBatchItem(
                lemma_id=lid,
                goal=f"{ctx.namespace}.ProblemSpec",
                blocker="telemetry failure batch",
                attempts=attempts[:4] if attempts else [("n/a", "failed")],
            )
        )
        seen.add(lid)
        if len(items) >= max_items:
            break
    return items


def append_task_cards(
    path: Path,
    *,
    ctx: ProblemContext,
    batch_id: str,
    split_into: list[str],
) -> list[str]:
    if not path.exists():
        raise RuntimeError(f"tasks file missing: {path}")
    text = path.read_text(encoding="utf-8")
    if "cards:" not in text:
        raise RuntimeError(f"tasks file malformed (missing `cards:`): {path}")

    existing_ids = parse_existing_task_ids(text)
    added_ids: list[str] = []
    new_lines: list[str] = []
    local_index = 1
    for item in split_into:
        card_id = normalize_card_id(item, local_index)
        while card_id in existing_ids:
            local_index += 1
            card_id = normalize_card_id(f"{card_id}_{local_index}", local_index)
        local_index += 1
        title = split_title(item, card_id)
        new_lines.extend(
            [
                f"  - id: {card_id}",
                f"    title: \"Planner split: {title}\"",
                "    depends_on: []",
                f"    lean_target: \"{ctx.namespace}.ProblemSpec\"",
                "    status: todo",
                f"    blocker: \"planner batch {batch_id}\"",
            ]
        )
        existing_ids.add(card_id)
        added_ids.append(card_id)

    if not new_lines:
        return added_ids

    if text and not text.endswith("\n"):
        text += "\n"
    text += "\n".join(new_lines) + "\n"
    path.write_text(text, encoding="utf-8")
    return added_ids


def upsert_planner_block(path: Path, *, batch_id: str, hints: list[str], required_defs: list[str]) -> None:
    if not path.exists():
        raise RuntimeError(f"sketch file missing: {path}")
    text = path.read_text(encoding="utf-8")
    marker_start = f"-- BEGIN PLANNER BATCH: {batch_id}"
    marker_end = f"-- END PLANNER BATCH: {batch_id}"
    ident = re.sub(r"[^A-Za-z0-9_]+", "_", batch_id).strip("_") or "batch"

    def as_lean_str(value: str) -> str:
        escaped = value.replace("\\", "\\\\").replace("\"", "\\\"")
        return f"\"{escaped}\""

    hint_lines = ",\n  ".join(as_lean_str(x) for x in hints) if hints else ""
    req_lines = ",\n  ".join(as_lean_str(x) for x in required_defs) if required_defs else ""
    block = (
        f"{marker_start}\n"
        f"/-- Planner hints imported from stuck batch `{batch_id}`. -/\n"
        f"def PlannerHints_{ident} : List String := [\n"
        f"  {hint_lines}\n"
        f"]\n\n"
        f"/-- Required definitions imported from stuck batch `{batch_id}`. -/\n"
        f"def PlannerRequiredDefs_{ident} : List String := [\n"
        f"  {req_lines}\n"
        f"]\n"
        f"{marker_end}\n"
    )

    if marker_start in text and marker_end in text:
        head, tail = text.split(marker_start, 1)
        _, rest = tail.split(marker_end, 1)
        new_text = head + block + rest.lstrip("\n")
    else:
        end_match = re.search(r"\nend\s+[A-Za-z0-9_.]+\s*\n?$", text)
        if end_match:
            idx = end_match.start()
            new_text = text[:idx].rstrip() + "\n\n" + block + "\n" + text[idx:].lstrip("\n")
        else:
            new_text = text.rstrip() + "\n\n" + block
    path.write_text(new_text, encoding="utf-8")


def has_placeholder(text: str) -> bool:
    return bool(PLACEHOLDER_RE.search(text))


def lean_noncomment_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.lstrip()
        if stripped.startswith("--"):
            continue
        lines.append((lineno, raw))
    return lines


def proved_token_violations(text: str) -> list[str]:
    violations: list[str] = []
    for lineno, line in lean_noncomment_lines(text):
        if SORRY_RE.search(line):
            violations.append(f"line {lineno}: contains `sorry`")
        if AXIOM_RE.search(line):
            violations.append(f"line {lineno}: contains `axiom`")
    return violations


def assert_proved_text_contract(text: str, *, label: str) -> None:
    violations = proved_token_violations(text)
    if not violations:
        return
    joined = "\n".join(f"- {v}" for v in violations[:12])
    raise RuntimeError(
        f"{label} must contain proved declarations only (no sorry/axiom).\n"
        f"{joined}"
    )


def assert_proved_file_contract(path: Path, *, label: str) -> None:
    if not path.exists():
        raise RuntimeError(f"{label} missing: {path}")
    text = path.read_text(encoding="utf-8")
    assert_proved_text_contract(text, label=label)


def insert_before_namespace_end(text: str, block: str) -> str:
    end_match = re.search(r"\nend\s+[A-Za-z0-9_.]+\s*\n?$", text)
    if end_match:
        idx = end_match.start()
        return text[:idx].rstrip() + "\n\n" + block.rstrip() + "\n\n" + text[idx:].lstrip("\n")
    return text.rstrip() + "\n\n" + block.rstrip() + "\n"


def extract_cache_promote_blocks(sketch_text: str) -> tuple[list[CachePromoteBlock], str]:
    blocks: list[CachePromoteBlock] = []
    new_lines: list[str] = []
    active_id: str | None = None
    active_lines: list[str] = []

    for idx, raw in enumerate(sketch_text.splitlines(), start=1):
        begin_match = CACHE_PROMOTE_BEGIN_RE.match(raw)
        if begin_match:
            if active_id is not None:
                raise RuntimeError(
                    f"nested CACHE_PROMOTE_BEGIN at line {idx}; current block `{active_id}` is not closed"
                )
            active_id = begin_match.group(1)
            active_lines = []
            continue

        end_match = CACHE_PROMOTE_END_RE.match(raw)
        if end_match:
            if active_id is None:
                raise RuntimeError(f"CACHE_PROMOTE_END at line {idx} without begin marker")
            end_id = end_match.group(1)
            if end_id != active_id:
                raise RuntimeError(
                    f"CACHE_PROMOTE_END id mismatch at line {idx}: begin `{active_id}`, end `{end_id}`"
                )
            content = "\n".join(active_lines).strip()
            if not content:
                raise RuntimeError(f"CACHE_PROMOTE block `{active_id}` is empty")
            assert_proved_text_contract(content, label=f"Sketch promote block `{active_id}`")
            blocks.append(CachePromoteBlock(block_id=active_id, content=content))
            new_lines.append(f"-- CACHE_PROMOTED: {active_id} (moved to Cache.lean)")
            active_id = None
            active_lines = []
            continue

        if active_id is not None:
            active_lines.append(raw)
            continue
        new_lines.append(raw)

    if active_id is not None:
        raise RuntimeError(f"CACHE_PROMOTE block `{active_id}` is not closed")
    return blocks, "\n".join(new_lines).rstrip() + "\n"


def markdown_table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|") or line.count("|") < 3:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        # table separator row like |---|---|
        if all(c and set(c) <= {"-", ":"} for c in cells):
            continue
        rows.append(cells)
    return rows


def validate_research_pack_quality(ctx: ProblemContext) -> list[str]:
    errors: list[str] = []

    sources_path = ctx.research_dir / "sources.md"
    glossary_path = ctx.research_dir / "glossary.yaml"
    outline_path = ctx.research_dir / "outline.md"
    lemmas_path = ctx.research_dir / "candidate_lemmas.md"
    gaps_path = ctx.research_dir / "gaps.md"

    sources_text = sources_path.read_text(encoding="utf-8")
    glossary_text = glossary_path.read_text(encoding="utf-8")
    outline_text = outline_path.read_text(encoding="utf-8")
    lemmas_text = lemmas_path.read_text(encoding="utf-8")
    gaps_text = gaps_path.read_text(encoding="utf-8")

    if has_placeholder(sources_text):
        errors.append("research/sources.md contains placeholder tokens (TODO/TBD/???)")
    source_rows = markdown_table_rows(sources_text)
    if len(source_rows) < 2:
        errors.append("research/sources.md must include at least one filled fact row")
    else:
        for i, row in enumerate(source_rows[1:], start=1):
            row_text = " | ".join(row)
            if has_placeholder(row_text):
                errors.append(f"research/sources.md row {i} still has placeholder tokens")
            # expected columns: fact_id | claim | source | location | confidence | notes
            if len(row) >= 4:
                source_col = row[2].strip()
                location_col = row[3].strip()
                if not source_col or source_col == "-":
                    errors.append(f"research/sources.md row {i} has empty source column")
                if not location_col or location_col == "-":
                    errors.append(f"research/sources.md row {i} has empty location column")

    if has_placeholder(glossary_text):
        errors.append("research/glossary.yaml contains placeholder tokens (TODO/TBD/???)")
    if "terms:" not in glossary_text:
        errors.append("research/glossary.yaml missing `terms` section")
    term_rows = [ln for ln in glossary_text.splitlines() if ln.strip().startswith("- term:")]
    if not term_rows:
        errors.append("research/glossary.yaml must provide at least one term mapping")

    if has_placeholder(outline_text):
        errors.append("research/outline.md contains placeholder tokens (TODO/TBD/???)")
    outline_steps = [
        ln for ln in outline_text.splitlines()
        if re.match(r"^\s*\d+\.\s+\S", ln)
    ]
    if len(outline_steps) < 3:
        errors.append("research/outline.md must include at least 3 numbered proof steps")

    if has_placeholder(lemmas_text):
        errors.append("research/candidate_lemmas.md contains placeholder tokens (TODO/TBD/???)")
    lemma_rows = markdown_table_rows(lemmas_text)
    if len(lemma_rows) < 2:
        errors.append("research/candidate_lemmas.md must include at least one lemma candidate row")

    if has_placeholder(gaps_text):
        errors.append("research/gaps.md contains placeholder tokens (TODO/TBD/???)")
    gap_rows = markdown_table_rows(gaps_text)
    if len(gap_rows) < 2:
        errors.append("research/gaps.md must include at least one gap row")

    return errors


def assert_research_pack_ready(ctx: ProblemContext) -> None:
    missing = [name for name in RESEARCH_FILES if not (ctx.research_dir / name).exists()]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            "Research Pack incomplete. Missing files: "
            f"{joined}. Run `intake_v2.py research-pack ...` first and fill the package."
        )
    quality_errors = validate_research_pack_quality(ctx)
    if quality_errors:
        details = "\n".join(f"- {msg}" for msg in quality_errors)
        raise RuntimeError(
            "Research Pack quality check failed. Fill the research files before Lean Commit:\n"
            f"{details}"
        )


def run_checked(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}")


def run_blocking_gates(repo_root: Path) -> None:
    gate_cmds: list[list[str]] = [
        ["lake", "build"],
        ["lake", "env", "lean", "Eval/ImportSmoke.lean"],
        ["lake", "env", "lean", "Eval/CanonicalAPISmoke.lean"],
        ["tools/ci/check_no_sorry_axiom.sh"],
        ["tools/ci/check_placeholder_policy.sh"],
        ["tools/ci/check_layer_imports.sh"],
        ["python3", "tools/ci/check_meta_index_graph_contract.py"],
        ["tools/ci/check_graph_ui_sync.sh"],
        ["tools/ci/check_graph_ui_source_sync.sh"],
        ["python3", "tools/docs/validate_ssot.py"],
        ["python3", "tools/docs/sync_docs.py", "--check"],
    ]
    for cmd in gate_cmds:
        run_checked(cmd, repo_root)


def load_domain_profiles(repo_root: Path) -> tuple[str, dict[str, DomainProfile]]:
    path = repo_root / "docs" / "meta" / "domains.yaml"
    data = parse_simple_yaml(path)

    module_roots = data.get("domain_module_roots")
    local_roots = data.get("domain_allowed_local_roots")
    concept_binds = data.get("domain_concept_binds")
    default_imports = data.get("domain_default_imports")
    mathlib_slice_roots = data.get("domain_mathlib_slice_roots")
    skills_whitelist = data.get("domain_skills_whitelist")
    bridge_modules = data.get("domain_bridge_modules")
    adjacent_domains = data.get("domain_adjacent_domains")
    default_domain = str(data.get("default_domain", "")).strip().lower()

    if not isinstance(module_roots, dict) or not module_roots:
        raise RuntimeError("docs/meta/domains.yaml missing `domain_module_roots`")
    if not isinstance(local_roots, dict) or not local_roots:
        raise RuntimeError("docs/meta/domains.yaml missing `domain_allowed_local_roots`")
    if concept_binds is not None and not isinstance(concept_binds, dict):
        raise RuntimeError("docs/meta/domains.yaml invalid `domain_concept_binds`")

    all_ids: set[str] = set()
    all_ids.update(k for k in module_roots if isinstance(k, str) and k)
    all_ids.update(k for k in local_roots if isinstance(k, str) and k)
    if concept_binds:
        all_ids.update(k for k in concept_binds if isinstance(k, str) and k)

    profiles: dict[str, DomainProfile] = {}
    for domain_id in sorted(all_ids):
        did = domain_id.lower()
        profile = DomainProfile(
            id=did,
            module_roots=as_str_list(module_roots.get(domain_id)),
            allowed_local_roots=as_str_list(local_roots.get(domain_id)),
            concept_binds=as_str_list(concept_binds.get(domain_id)) if isinstance(concept_binds, dict) else [],
            default_imports=as_str_list(default_imports.get(domain_id)) if isinstance(default_imports, dict) else [],
            mathlib_slice_roots=as_str_list(mathlib_slice_roots.get(domain_id))
            if isinstance(mathlib_slice_roots, dict)
            else [],
            skills_whitelist=as_str_list(skills_whitelist.get(domain_id))
            if isinstance(skills_whitelist, dict)
            else [],
            bridge_modules=as_str_list(bridge_modules.get(domain_id)) if isinstance(bridge_modules, dict) else [],
            adjacent_domains=as_str_list(adjacent_domains.get(domain_id))
            if isinstance(adjacent_domains, dict)
            else [],
        )
        profiles[did] = profile

    if not default_domain or default_domain not in profiles:
        default_domain = sorted(profiles)[0] if profiles else "learning"
    return default_domain, profiles


def validate_domain_ids(domains: list[str], profiles: dict[str, DomainProfile]) -> list[str]:
    unknown = [d for d in domains if d not in profiles]
    if unknown:
        known = ", ".join(sorted(profiles))
        bad = ", ".join(sorted(unknown))
        raise RuntimeError(
            f"unknown domain(s): {bad}. known domains from docs/meta/domains.yaml: {known}"
        )
    return domains


def parse_taxonomy_node_ids(path: Path) -> set[str]:
    data = parse_simple_yaml(path)
    nodes = data.get("nodes")
    node_ids: set[str] = set()
    if isinstance(nodes, list):
        for row in nodes:
            if isinstance(row, dict):
                nid = row.get("id")
                if isinstance(nid, str) and nid:
                    node_ids.add(nid)
    return node_ids


def parse_taxonomy_bindings(path: Path) -> set[tuple[str, str]]:
    data = parse_simple_yaml(path)
    rows = data.get("bindings")
    pairs: set[tuple[str, str]] = set()
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            target = row.get("target")
            node = row.get("node")
            if isinstance(target, str) and isinstance(node, str) and target and node:
                pairs.add((target, node))
    return pairs


def append_taxonomy_binding(path: Path, *, target: str, node: str) -> bool:
    existing = parse_taxonomy_bindings(path)
    if (target, node) in existing:
        return False

    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if "bindings:" not in text:
        if text and not text.endswith("\n"):
            text += "\n"
        text += "\nbindings:\n"
    if text and not text.endswith("\n"):
        text += "\n"
    text += f"  - target: {target}\n"
    text += "    kind: module\n"
    text += f"    node: {node}\n"
    text += "    spine: true\n"
    path.write_text(text, encoding="utf-8")
    return True


def normalize_alias_phrase(raw: str) -> str:
    phrase = re.sub(r"[^\w\s]+", " ", raw.strip(), flags=re.UNICODE)
    phrase = phrase.replace("_", " ")
    phrase = re.sub(r"\s+", " ", phrase)
    phrase = phrase.strip()
    return phrase.lower()


def alias_phrases(ctx: ProblemContext) -> list[str]:
    seeds = [
        normalize_alias_phrase(ctx.problem_title),
        normalize_alias_phrase(ctx.problem_slug.replace("_", " ")),
        normalize_alias_phrase(f"{ctx.domain_tag} {ctx.problem_slug.replace('_', ' ')}"),
    ]
    out: list[str] = []
    seen: set[str] = set()
    for phrase in seeds:
        if not phrase or phrase in seen:
            continue
        seen.add(phrase)
        out.append(phrase)
    return out


def rewrite_aliases(path: Path, aliases: dict[str, list[str]]) -> None:
    data = parse_simple_yaml(path)
    version = str(data.get("version", "1"))
    description = str(
        data.get("description", "Minimal retrieval aliases for MLTheory intake workflow.")
    )

    lines = [f"version: {safe_yaml_scalar(version)}", f"description: {safe_yaml_scalar(description)}", "aliases:"]
    for key in sorted(aliases):
        values = sorted(set(as_str_list(aliases[key])))
        lines.append(f"  {safe_yaml_key(key)}:")
        for val in values:
            lines.append(f"    - {safe_yaml_scalar(val)}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_aliases(path: Path, *, module_target: str, phrases: list[str]) -> bool:
    data = parse_simple_yaml(path)
    aliases = data.get("aliases") if isinstance(data.get("aliases"), dict) else {}
    changed = False

    for phrase in phrases:
        current = set(as_str_list(aliases.get(phrase)))
        if module_target not in current:
            current.add(module_target)
            aliases[phrase] = sorted(current)
            changed = True

    if changed:
        rewrite_aliases(path, aliases)
    return changed


def choose_concept_nodes(
    domains: list[str],
    domain_profiles: dict[str, DomainProfile],
    taxonomy_nodes: set[str],
) -> list[str]:
    selected: list[str] = []
    seen: set[str] = set()

    for domain in domains:
        profile = domain_profiles.get(domain)
        if profile is None:
            continue
        for bind in profile.concept_binds:
            if bind in taxonomy_nodes and bind not in seen:
                seen.add(bind)
                selected.append(bind)
                break

    if selected:
        return selected
    if "methods" in taxonomy_nodes:
        return ["methods"]
    if "mltheory" in taxonomy_nodes:
        return ["mltheory"]
    return []


def sync_taxonomy_aliases(ctx: ProblemContext, domain_profiles: dict[str, DomainProfile]) -> None:
    taxonomy_path = ctx.repo_root / "docs" / "meta" / "taxonomy.yaml"
    aliases_path = ctx.repo_root / "docs" / "meta" / "aliases.yaml"

    taxonomy_nodes = parse_taxonomy_node_ids(taxonomy_path)
    concept_nodes = choose_concept_nodes(ctx.domains, domain_profiles, taxonomy_nodes)
    for node in concept_nodes:
        append_taxonomy_binding(taxonomy_path, target=ctx.spec_module, node=node)

    phrases = alias_phrases(ctx)
    if phrases:
        update_aliases(aliases_path, module_target=ctx.spec_module, phrases=phrases)


def append_telemetry_event(
    ctx: ProblemContext,
    event: str,
    *,
    success: bool,
    extra: dict[str, object] | None = None,
) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "problem_id": ctx.problem_id,
        "domains": ctx.domains,
        "goal_shape": "Prop",
        "module": ctx.spec_module,
        "tactic": "trivial",
        "success": success,
    }
    if extra:
        payload.update(extra)
    path = ctx.problem_dir / "Telemetry.jsonl"
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def stage_research_pack(ctx: ProblemContext, *, force: bool) -> None:
    write_if_missing(ctx.problem_dir / "statement.md", render_statement(ctx), force=force)
    write_if_missing(ctx.problem_dir / "Blueprint.md", render_blueprint(ctx), force=force)
    write_if_missing(ctx.research_dir / "sources.md", render_sources_md(ctx), force=force)
    write_if_missing(ctx.research_dir / "glossary.yaml", render_glossary_yaml(ctx), force=force)
    write_if_missing(ctx.research_dir / "outline.md", render_outline_md(ctx), force=force)
    write_if_missing(
        ctx.research_dir / "candidate_lemmas.md",
        render_candidate_lemmas_md(ctx),
        force=force,
    )
    write_if_missing(ctx.research_dir / "gaps.md", render_gaps_md(ctx), force=force)
    write_if_missing(
        ctx.problem_dir / "stuck_batches" / "batch-001.yaml",
        render_stuck_batch_yaml(ctx, "batch-001"),
        force=force,
    )
    write_if_missing(
        ctx.problem_dir / "intake_manifest.json",
        render_manifest(ctx, "research_pack_ready"),
        force=True,
    )


def stage_lean_commit(
    ctx: ProblemContext,
    *,
    force: bool,
    run_artifacts: bool,
    domain_profiles: dict[str, DomainProfile],
) -> None:
    assert_research_pack_ready(ctx)

    write_if_missing(ctx.problem_dir / "Spec.lean", render_spec_lean(ctx), force=force)
    write_if_missing(ctx.problem_dir / "Sketch.lean", render_sketch_lean(ctx), force=force)
    write_if_missing(ctx.problem_dir / "Cache.lean", render_cache_lean(ctx), force=force)
    write_if_missing(ctx.problem_dir / "Tasks.yaml", render_tasks_yaml(ctx), force=force)
    write_if_missing(
        ctx.problem_dir / "stuck_batches" / "batch-001.yaml",
        render_stuck_batch_yaml(ctx, "batch-001"),
        force=force,
    )
    write_if_missing(ctx.problem_dir / "Telemetry.jsonl", "", force=False)

    spec_path = ctx.problem_dir / "Spec.lean"
    cache_path = ctx.problem_dir / "Cache.lean"
    sketch_path = ctx.problem_dir / "Sketch.lean"
    assert_proved_file_contract(spec_path, label="Spec.lean")
    assert_proved_file_contract(cache_path, label="Cache.lean")

    # Lean Commit stage: files must compile before metadata/artifact updates.
    run_checked(["lake", "env", "lean", str(spec_path)], ctx.repo_root)
    run_checked(["lake", "env", "lean", str(cache_path)], ctx.repo_root)
    run_checked(["lake", "env", "lean", str(sketch_path)], ctx.repo_root)

    sync_taxonomy_aliases(ctx, domain_profiles)

    if run_artifacts:
        run_checked(["tools/index/gen_mltheory_index.sh"], ctx.repo_root)
        run_checked(["tools/index/gen_graph_artifacts.sh"], ctx.repo_root)

    # Lean Commit contract: must pass the repository blocking gate.
    run_blocking_gates(ctx.repo_root)

    append_telemetry_event(ctx, "lean_commit_ready", success=True)
    write_if_missing(
        ctx.problem_dir / "intake_manifest.json",
        render_manifest(ctx, "lean_commit_ready"),
        force=True,
    )


def stage_stuck_batch(
    ctx: ProblemContext,
    *,
    batch_id: str,
    force: bool,
    auto_from_tasks: bool,
    max_items: int,
) -> None:
    if not ctx.problem_dir.exists():
        raise RuntimeError(
            f"problem directory does not exist: {ctx.problem_dir}. "
            "Run research-pack/lean-commit first."
        )

    batch_name = normalize_batch_id(batch_id)
    batch_path = ctx.problem_dir / "stuck_batches" / f"{batch_name}.yaml"
    item_count = 1
    if auto_from_tasks:
        items = collect_auto_stuck_items(ctx, max_items=max_items)
        if not items:
            raise RuntimeError(
                "stuck-batch auto mode found no blocked cards. "
                "Mark cards as `status: blocked|stuck` (or set non-empty blocker) in Tasks.yaml "
                "or pass --stuck-template to generate a manual template."
            )
        if batch_path.exists() and not force:
            raise RuntimeError(
                f"stuck batch already exists: {batch_path}. "
                "Use --force to overwrite or choose a new --batch-id."
            )
        ensure_parent(batch_path)
        batch_path.write_text(
            render_stuck_batch_yaml(ctx, batch_name, items=items),
            encoding="utf-8",
        )
        item_count = len(items)
    else:
        write_if_missing(batch_path, render_stuck_batch_yaml(ctx, batch_name), force=force)

    append_telemetry_event(
        ctx,
        "replan_batch_opened",
        success=True,
        extra={"batch_id": batch_name, "item_count": item_count},
    )


def stage_apply_replan(
    ctx: ProblemContext,
    *,
    batch_id: str,
) -> None:
    if not ctx.problem_dir.exists():
        raise RuntimeError(
            f"problem directory does not exist: {ctx.problem_dir}. "
            "Run research-pack/lean-commit first."
        )
    batch_name = normalize_batch_id(batch_id)
    batch_path = ctx.problem_dir / "stuck_batches" / f"{batch_name}.yaml"
    if not batch_path.exists():
        raise RuntimeError(
            f"stuck batch file missing: {batch_path}. "
            "Run `intake_v2.py stuck-batch ...` first or provide a valid batch id."
        )

    parsed = parse_stuck_batch_file(batch_path)
    split_into = parsed["split_into"]
    hints = parsed["hints"]
    required_defs = parsed["required_defs"]
    item_lemma_ids = parsed["item_lemma_ids"]
    if not split_into and not hints and not required_defs:
        raise RuntimeError(
            f"planner_reply in {batch_path} is empty. Fill split_into/hints/required_defs before apply-replan."
        )

    tasks_path = ctx.problem_dir / "Tasks.yaml"
    sketch_path = ctx.problem_dir / "Sketch.lean"
    spec_path = ctx.problem_dir / "Spec.lean"
    cache_path = ctx.problem_dir / "Cache.lean"
    assert_proved_file_contract(spec_path, label="Spec.lean")
    assert_proved_file_contract(cache_path, label="Cache.lean")

    added_card_ids = append_task_cards(
        tasks_path,
        ctx=ctx,
        batch_id=batch_name,
        split_into=split_into,
    )
    upsert_planner_block(
        sketch_path,
        batch_id=batch_name,
        hints=hints,
        required_defs=required_defs,
    )

    run_checked(["lake", "env", "lean", str(spec_path)], ctx.repo_root)
    run_checked(["lake", "env", "lean", str(cache_path)], ctx.repo_root)
    run_checked(["lake", "env", "lean", str(sketch_path)], ctx.repo_root)

    applied_payload = {
        "version": 1,
        "batch_id": batch_name,
        "problem_id": ctx.problem_id,
        "domains": ctx.domains,
        "item_lemma_ids": item_lemma_ids,
        "split_into": split_into,
        "hints": hints,
        "required_defs": required_defs,
        "added_task_cards": added_card_ids,
        "applied_at": datetime.now(timezone.utc).isoformat(),
    }
    applied_path = ctx.problem_dir / "stuck_batches" / f"{batch_name}.applied.json"
    applied_path.write_text(json.dumps(applied_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_telemetry_event(ctx, "replan_batch_applied", success=True)
    write_if_missing(
        ctx.problem_dir / "intake_manifest.json",
        render_manifest(ctx, "replan_batch_applied"),
        force=True,
    )


def stage_promote_cache(
    ctx: ProblemContext,
    *,
    run_artifacts: bool,
) -> None:
    if not ctx.problem_dir.exists():
        raise RuntimeError(
            f"problem directory does not exist: {ctx.problem_dir}. "
            "Run research-pack/lean-commit first."
        )

    spec_path = ctx.problem_dir / "Spec.lean"
    cache_path = ctx.problem_dir / "Cache.lean"
    sketch_path = ctx.problem_dir / "Sketch.lean"
    tasks_path = ctx.problem_dir / "Tasks.yaml"
    for required in (spec_path, cache_path, sketch_path, tasks_path):
        if not required.exists():
            raise RuntimeError(f"promote-cache requires file: {required}")

    sketch_text = sketch_path.read_text(encoding="utf-8")
    blocks, rewritten_sketch = extract_cache_promote_blocks(sketch_text)
    if not blocks:
        raise RuntimeError(
            "promote-cache found no markers in Sketch.lean. "
            "Add blocks using `-- CACHE_PROMOTE_BEGIN: <id>` / `-- CACHE_PROMOTE_END: <id>`."
        )

    cache_text = cache_path.read_text(encoding="utf-8")
    promoted_ids: list[str] = []
    for block in blocks:
        marker = f"-- CACHE_PROMOTED: {block.block_id}"
        if marker in cache_text:
            continue
        inserted = f"{marker}\n{block.content}"
        cache_text = insert_before_namespace_end(cache_text, inserted)
        promoted_ids.append(block.block_id)

    cache_path.write_text(cache_text, encoding="utf-8")
    sketch_path.write_text(rewritten_sketch, encoding="utf-8")

    assert_proved_file_contract(spec_path, label="Spec.lean")
    assert_proved_file_contract(cache_path, label="Cache.lean")

    run_checked(["lake", "env", "lean", str(spec_path)], ctx.repo_root)
    run_checked(["lake", "env", "lean", str(cache_path)], ctx.repo_root)
    run_checked(["lake", "env", "lean", str(sketch_path)], ctx.repo_root)

    if run_artifacts:
        run_checked(["tools/index/gen_mltheory_index.sh"], ctx.repo_root)
        run_checked(["tools/index/gen_graph_artifacts.sh"], ctx.repo_root)

    run_blocking_gates(ctx.repo_root)
    append_telemetry_event(
        ctx,
        "cache_promoted",
        success=True,
        extra={"promoted_block_count": len(promoted_ids), "promoted_blocks": promoted_ids},
    )
    write_if_missing(
        ctx.problem_dir / "intake_manifest.json",
        render_manifest(ctx, "cache_promoted"),
        force=True,
    )


def stage_proof_scope(ctx: ProblemContext, *, domain_profiles: dict[str, DomainProfile]) -> None:
    if not ctx.problem_dir.exists():
        raise RuntimeError(
            f"problem directory does not exist: {ctx.problem_dir}. "
            "Run research-pack/lean-commit first."
        )

    required = ("Spec.lean", "Cache.lean", "Sketch.lean", "Tasks.yaml")
    missing = [name for name in required if not (ctx.problem_dir / name).exists()]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            "proof-scope requires Lean Commit outputs. Missing files: "
            f"{joined}. Run `intake_v2.py lean-commit ...` first."
        )

    # Proof scope stage: verify core Lean files compile before retrieval/proving loops.
    spec_path = ctx.problem_dir / "Spec.lean"
    cache_path = ctx.problem_dir / "Cache.lean"
    sketch_path = ctx.problem_dir / "Sketch.lean"
    assert_proved_file_contract(spec_path, label="Spec.lean")
    assert_proved_file_contract(cache_path, label="Cache.lean")
    run_checked(["lake", "env", "lean", str(spec_path)], ctx.repo_root)
    run_checked(["lake", "env", "lean", str(cache_path)], ctx.repo_root)
    run_checked(["lake", "env", "lean", str(sketch_path)], ctx.repo_root)

    active_domain = ctx.domains[0]
    profile = domain_profiles.get(active_domain)
    if profile is None:
        known = ", ".join(sorted(domain_profiles))
        raise RuntimeError(f"active domain `{active_domain}` not found. known domains: {known}")

    payload = {
        "version": 1,
        "problem_id": ctx.problem_id,
        "problem_title": ctx.problem_title,
        "namespace": ctx.namespace,
        "domains": ctx.domains,
        "active_domain": active_domain,
        "widening_path": [
            "domain_local",
            "domain_mathlib_slice",
            "adjacent_domains",
            "full_mltheory",
            "full_mathlib",
            "external_semantic",
        ],
        "domain_profile": {
            "module_roots": profile.module_roots,
            "allowed_local_roots": profile.allowed_local_roots,
            "default_imports": profile.default_imports,
            "mathlib_slice_roots": profile.mathlib_slice_roots,
            "skills_whitelist": profile.skills_whitelist,
            "bridge_modules": profile.bridge_modules,
            "adjacent_domains": profile.adjacent_domains,
        },
        "status": "proof_scope_ready",
        "generated_at": str(date.today()),
    }
    scope_path = ctx.problem_dir / "proof_scope.json"
    scope_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_telemetry_event(ctx, "proof_scope_ready", success=True)
    write_if_missing(
        ctx.problem_dir / "intake_manifest.json",
        render_manifest(ctx, "proof_scope_ready"),
        force=True,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="MLTheory Intake v2 helper")
    ap.add_argument(
        "phase",
        choices=["research-pack", "lean-commit", "stuck-batch", "apply-replan", "promote-cache", "proof-scope"],
        help="pipeline stage",
    )
    ap.add_argument("--domain", required=True, help="domain name (e.g. learning)")
    ap.add_argument("--problem", required=True, help="problem name")
    ap.add_argument("--title", default="Untitled Problem", help="human-readable problem title")
    ap.add_argument(
        "--statement-file",
        default="",
        help="optional statement file path for domain inference signals",
    )
    ap.add_argument(
        "--domains",
        default="",
        help="comma-separated domain tags for Tasks/metadata (default uses primary domain)",
    )
    ap.add_argument("--repo-root", default=".", help="repository root path")
    ap.add_argument("--force", action="store_true", help="overwrite existing template files")
    ap.add_argument(
        "--skip-artifacts",
        action="store_true",
        help="skip index/graph regeneration in lean-commit/promote-cache stages",
    )
    ap.add_argument(
        "--batch-id",
        default="batch-001",
        help="stuck batch id for phases `stuck-batch`/`apply-replan` (default: batch-001)",
    )
    ap.add_argument(
        "--stuck-template",
        action="store_true",
        help="for phase `stuck-batch`, write a manual template instead of auto-collecting blocked cards",
    )
    ap.add_argument(
        "--max-stuck-items",
        type=int,
        default=12,
        help="max auto-collected blocked cards in phase `stuck-batch` (default: 12)",
    )
    # backward compatible no-op alias
    ap.add_argument("--run-artifacts", action="store_true", help=argparse.SUPPRESS)
    return ap


def main() -> int:
    args = build_arg_parser().parse_args()

    repo_root = Path(args.repo_root).resolve()
    default_domain, domain_profiles = load_domain_profiles(repo_root)
    statement_text = ""
    if args.statement_file:
        statement_path = Path(args.statement_file)
        if not statement_path.is_absolute():
            statement_path = (repo_root / statement_path).resolve()
        if not statement_path.exists():
            raise RuntimeError(f"statement file not found: {statement_path}")
        statement_text = statement_path.read_text(encoding="utf-8")

    problem_mod = slug_to_module(args.problem)
    problem_slug = slug_to_id(args.problem, fallback=problem_mod.lower())
    title = args.title.strip() or "Untitled Problem"
    domains, domains_guess, domain_confidence, inference_mode = infer_domains(
        domain_hint=args.domain,
        explicit_domains_raw=args.domains,
        default_domain=default_domain,
        profiles=domain_profiles,
        problem_slug=problem_slug,
        title=title,
        statement_text=statement_text,
    )
    domains = validate_domain_ids(domains, domain_profiles)
    primary_domain = domains[0]

    domain_mod = slug_to_module(primary_domain)

    ctx = ProblemContext(
        repo_root=repo_root,
        domain_tag=primary_domain,
        domain_module=domain_mod,
        problem=problem_mod,
        problem_slug=problem_slug,
        problem_title=title,
        domains=domains,
        domains_guess=domains_guess,
        domain_confidence=domain_confidence,
        domain_inference_mode=inference_mode,
    )

    run_artifacts = not args.skip_artifacts

    if args.phase == "research-pack":
        stage_research_pack(ctx, force=args.force)
    elif args.phase == "lean-commit":
        stage_lean_commit(
            ctx,
            force=args.force,
            run_artifacts=run_artifacts,
            domain_profiles=domain_profiles,
        )
    elif args.phase == "stuck-batch":
        stage_stuck_batch(
            ctx,
            batch_id=args.batch_id,
            force=args.force,
            auto_from_tasks=not args.stuck_template,
            max_items=max(1, args.max_stuck_items),
        )
    elif args.phase == "apply-replan":
        stage_apply_replan(ctx, batch_id=args.batch_id)
    elif args.phase == "promote-cache":
        stage_promote_cache(ctx, run_artifacts=not args.skip_artifacts)
    else:
        stage_proof_scope(ctx, domain_profiles=domain_profiles)

    print(
        f"[intake_v2] phase={args.phase} ready at {ctx.problem_dir} "
        f"(namespace={ctx.namespace}, domains={ctx.domains}, domains_guess={ctx.domains_guess}, "
        f"domain_confidence={ctx.domain_confidence}, mode={ctx.domain_inference_mode}, "
        f"artifacts={run_artifacts}, batch_id={args.batch_id})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
