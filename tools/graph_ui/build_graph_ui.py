#!/usr/bin/env python3
"""Render GraphExplorer HTML from graph_ui source template + app script/parts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "tools" / "graph_ui" / "src" / "index.template.html"
APP_JS = ROOT / "tools" / "graph_ui" / "src" / "app.js"
APP_PARTS_DIR = ROOT / "tools" / "graph_ui" / "src" / "app"
DOC_OUT = ROOT / "docs" / "GraphExplorer.html"
DIST_OUT = ROOT / "tools" / "graph_ui" / "dist" / "index.html"
PLACEHOLDER = "__GRAPH_EXPLORER_APP__"


def load_app_js() -> str:
    if APP_PARTS_DIR.exists():
        parts = sorted(p for p in APP_PARTS_DIR.glob("*.js") if p.is_file())
        if parts:
            chunks = [p.read_text(encoding="utf-8").rstrip("\n") for p in parts]
            return "\n\n".join(chunks).rstrip("\n") + "\n"
    if APP_JS.exists():
        return APP_JS.read_text(encoding="utf-8").rstrip("\n") + "\n"
    raise RuntimeError(f"missing app source: {APP_PARTS_DIR} and {APP_JS}")


def render_html(template_path: Path, app_js: str) -> str:
    if not template_path.exists():
        raise RuntimeError(f"missing template: {template_path}")
    template = template_path.read_text(encoding="utf-8")
    app_js = app_js.rstrip("\n")
    if PLACEHOLDER not in template:
        raise RuntimeError(f"template missing placeholder `{PLACEHOLDER}`: {template_path}")
    rendered = template.replace(PLACEHOLDER, app_js)
    if not rendered.endswith("\n"):
        rendered += "\n"
    return rendered


def ensure_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build GraphExplorer HTML from source template")
    ap.add_argument("--check", action="store_true", help="verify docs/dist are in sync with source template")
    ap.add_argument("--write", action="store_true", help="write rendered HTML to docs/dist outputs")
    args = ap.parse_args()

    app_js = load_app_js()
    rendered = render_html(TEMPLATE, app_js)
    if args.check:
        ok = True
        if APP_JS.exists():
            current_app = APP_JS.read_text(encoding="utf-8")
            if current_app != app_js:
                print(f"[build_graph_ui] out of sync: {APP_JS.relative_to(ROOT)}")
                ok = False
        for path in (DOC_OUT, DIST_OUT):
            if not path.exists():
                print(f"[build_graph_ui] missing output: {path.relative_to(ROOT)}")
                ok = False
                continue
            current = path.read_text(encoding="utf-8")
            if current != rendered:
                print(f"[build_graph_ui] out of sync: {path.relative_to(ROOT)}")
                ok = False
        if ok:
            print("[build_graph_ui] check passed.")
            return 0
        return 1

    # default mode is write
    ensure_write(APP_JS, app_js)
    ensure_write(DOC_OUT, rendered)
    ensure_write(DIST_OUT, rendered)
    print(
        "[build_graph_ui] wrote "
        f"{APP_JS.relative_to(ROOT)}, {DOC_OUT.relative_to(ROOT)} and {DIST_OUT.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
