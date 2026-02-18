#!/usr/bin/env python3
"""Append a usage telemetry event to local jsonl storage."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--event-file",
        type=Path,
        default=Path("artifacts/telemetry/usage_events.jsonl"),
        help="usage events jsonl path",
    )
    ap.add_argument(
        "--decl",
        action="append",
        default=[],
        help="used declaration name (repeat for multiple decls)",
    )
    ap.add_argument("--module", type=str, default="", help="active module")
    ap.add_argument("--task", type=str, default="", help="task card identifier")
    ap.add_argument(
        "--status",
        type=str,
        choices=["success", "failure"],
        default="success",
        help="event status",
    )
    ap.add_argument("--source", type=str, default="manual", help="event source")
    ap.add_argument("--note", type=str, default="", help="optional note")
    args = ap.parse_args()

    used_decls = sorted({d.strip() for d in args.decl if d and d.strip()})
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": args.status,
        "source": args.source,
        "module": args.module,
        "task": args.task,
        "used_decls": used_decls,
        "note": args.note,
    }

    out = args.event_file.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(
        f"[record_usage] wrote event to {out} "
        f"(decls={len(used_decls)}, status={args.status})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
