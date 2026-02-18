#!/usr/bin/env python3
"""Check review-oriented derived views consistency from SSOT."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "ssot" / "registry.json"
DASHBOARD = ROOT / "docs" / "ReviewDashboard.md"
API_CARDS = ROOT / "docs" / "APICards.md"
TOOL_FOREST_HTML = ROOT / "docs" / "ToolForestInteractive.html"
INDEX_DOC = ROOT / "docs" / "INDEX.md"

PROMOTION_DECISION_RE = re.compile(
    r"`([^`]+)` Already from planned_modules elevated to reality file-backed module"
)


def extract_recent_promotions(decisions: list[dict], limit: int = 8) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for row in reversed(decisions):
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


def require_markers(text: str, markers: list[str], label: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{label}: missing marker `{marker}`")


def main() -> int:
    errors: list[str] = []

    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    decisions = data.get("decisions", [])
    modules = data.get("modules", [])

    if not DASHBOARD.exists():
        errors.append("docs/ReviewDashboard.md missing")
    if not API_CARDS.exists():
        errors.append("docs/APICards.md missing")
    if not TOOL_FOREST_HTML.exists():
        errors.append("docs/ToolForestInteractive.html missing")
    if not INDEX_DOC.exists():
        errors.append("docs/INDEX.md missing")

    if errors:
        print("[check_review_views_consistency] failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    dashboard = DASHBOARD.read_text(encoding="utf-8")
    api_cards = API_CARDS.read_text(encoding="utf-8")
    html = TOOL_FOREST_HTML.read_text(encoding="utf-8")
    index_doc = INDEX_DOC.read_text(encoding="utf-8")

    require_markers(
        dashboard,
        [
            "# Acceptance Kanban(Review Dashboard)",
            "## Look at these four things first",
            "## Recently promoted(planned -> file-backed)",
            "## Current execution focus(execution_backlog)",
            "## One-click acceptance command",
        ],
        "ReviewDashboard.md",
        errors,
    )

    require_markers(
        api_cards,
        [
            "# smallest API card(APICards)",
            "## How to use(2 minute)",
            "## See recent changes first",
            "## View by area(public module)",
        ],
        "APICards.md",
        errors,
    )

    require_markers(
        index_doc,
        [
            "[ReviewDashboard.md](./ReviewDashboard.md)",
            "[APICards.md](./APICards.md)",
            "check_review_views_consistency.py",
        ],
        "INDEX.md",
        errors,
    )

    # Public module cards must all be present for inspection completeness.
    for mod in modules:
        if mod.get("user_surface") != "public":
            continue
        mpath = mod.get("module_path")
        if isinstance(mpath, str) and mpath not in api_cards:
            errors.append(f"APICards.md missing public module `{mpath}`")

    # Latest promotions should appear in dashboard.
    for mpath in extract_recent_promotions(decisions, limit=5):
        if mpath not in dashboard:
            errors.append(f"ReviewDashboard.md missing recent promoted module `{mpath}`")

    # Interactive defaults and quick presets.
    require_markers(
        html,
        [
            'option value="real" selected',
            "const MAX_ROWS = 120;",
            'id="preset-real"',
            'id="preset-near"',
            'id="preset-all"',
        ],
        "ToolForestInteractive.html",
        errors,
    )

    if errors:
        print("[check_review_views_consistency] failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("[check_review_views_consistency] passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
