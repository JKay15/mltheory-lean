#!/usr/bin/env python3
"""Problem Suite runner for Intake v2."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class SuiteProblem:
    problem_id: str
    title: str
    domain: str
    domains: str
    statement_file: str
    success_criteria: str


def parse_scalar(raw: str) -> str:
    text = raw.strip()
    if not text:
        return ""
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    return text


def parse_suite_yaml(path: Path) -> dict:
    if not path.exists():
        raise RuntimeError(f"suite file not found: {path}")

    data: dict = {"problems": []}
    section = ""
    current: dict | None = None

    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            s = line.strip()

            if indent == 0:
                current = None
                if s == "problems:":
                    section = "problems"
                    continue
                section = ""
                if ":" in s:
                    k, v = s.split(":", 1)
                    data[k.strip()] = parse_scalar(v)
                continue

            if section == "problems":
                if s.startswith("- "):
                    current = {}
                    data["problems"].append(current)
                    tail = s[2:].strip()
                    if ":" in tail:
                        k, v = tail.split(":", 1)
                        current[k.strip()] = parse_scalar(v)
                    continue
                if current is not None and ":" in s:
                    k, v = s.split(":", 1)
                    current[k.strip()] = parse_scalar(v)

    if not isinstance(data.get("problems"), list):
        raise RuntimeError("suite.yaml: `problems` must be a list")
    return data


def suite_problems(raw: dict) -> list[SuiteProblem]:
    out: list[SuiteProblem] = []
    default_domain = str(raw.get("default_domain", "learning")).strip() or "learning"
    default_domains = str(raw.get("default_domains", default_domain)).strip() or default_domain

    for i, row in enumerate(raw.get("problems", [])):
        if not isinstance(row, dict):
            raise RuntimeError(f"suite.yaml: problems[{i}] must be mapping")
        pid = str(row.get("id", "")).strip()
        if not pid:
            raise RuntimeError(f"suite.yaml: problems[{i}] missing id")
        title = str(row.get("title", pid)).strip() or pid
        domain = str(row.get("domain", default_domain)).strip() or default_domain
        domains = str(row.get("domains", default_domains)).strip() or default_domains
        statement_file = str(row.get("statement_file", "")).strip()
        success_criteria = str(row.get("success_criteria", "spec_only")).strip() or "spec_only"
        out.append(
            SuiteProblem(
                problem_id=pid,
                title=title,
                domain=domain,
                domains=domains,
                statement_file=statement_file,
                success_criteria=success_criteria,
            )
        )
    return out


def run_checked(cmd: list[str], cwd: Path, *, dry_run: bool) -> None:
    if dry_run:
        print("[dry-run]", " ".join(cmd))
        return
    proc = subprocess.run(cmd, cwd=str(cwd), check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}")


def intake_cmd(
    *,
    phase: str,
    problem: SuiteProblem,
    repo_root: Path,
    batch_id: str,
    skip_artifacts: bool,
) -> list[str]:
    cmd = [
        "python3",
        "tools/intake/intake_v2.py",
        phase,
        "--domain",
        problem.domain,
        "--problem",
        problem.problem_id,
        "--title",
        problem.title,
    ]
    if problem.domains:
        cmd.extend(["--domains", problem.domains])
    if problem.statement_file:
        cmd.extend(["--statement-file", problem.statement_file])
    if phase in {"stuck-batch", "apply-replan"}:
        cmd.extend(["--batch-id", batch_id])
    if phase in {"lean-commit", "promote-cache"} and skip_artifacts:
        cmd.append("--skip-artifacts")
    return cmd


def write_run_summary(
    *,
    suite_path: Path,
    phase: str,
    problems: list[SuiteProblem],
    dry_run: bool,
) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "suite": str(suite_path),
        "phase": phase,
        "problem_count": len(problems),
        "problems": [
            {
                "id": p.problem_id,
                "title": p.title,
                "domain": p.domain,
                "domains": p.domains,
                "success_criteria": p.success_criteria,
            }
            for p in problems
        ],
        "dry_run": dry_run,
    }
    out = suite_path.parent / "suite_run.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cmd_init(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    suite_dir = repo_root / "suites" / args.suite_id
    suite_yaml = suite_dir / "suite.yaml"
    problems_dir = suite_dir / "problems"

    if suite_yaml.exists() and not args.force:
        raise RuntimeError(f"suite already exists: {suite_yaml} (use --force to overwrite)")

    problems_dir.mkdir(parents=True, exist_ok=True)
    sample_dir = problems_dir / "concentration_gap"
    sample_dir.mkdir(parents=True, exist_ok=True)
    (sample_dir / "statement.md").write_text(
        "# Statement\n\nPaste the original statement and references here.\n",
        encoding="utf-8",
    )

    template = f"""version: 1
suite_id: {args.suite_id}
description: TODO
default_domain: learning
default_domains: learning
problems:
  - id: concentration_gap
    title: Concentration Gap Problem
    domain: learning
    domains: learning,probability
    statement_file: suites/{args.suite_id}/problems/concentration_gap/statement.md
    success_criteria: spec_only
"""
    suite_yaml.write_text(template, encoding="utf-8")
    print(f"[problem_suite] created {suite_yaml}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    suite_path = Path(args.suite)
    if not suite_path.is_absolute():
        suite_path = (repo_root / suite_path).resolve()

    raw = parse_suite_yaml(suite_path)
    problems = suite_problems(raw)
    if not problems:
        raise RuntimeError("suite.yaml has no problems")

    phase = args.phase
    batch_id = args.batch_id
    skip_per_problem_artifacts = phase in {"lean-commit", "promote-cache"}

    for problem in problems:
        cmd = intake_cmd(
            phase=phase,
            problem=problem,
            repo_root=repo_root,
            batch_id=batch_id,
            skip_artifacts=skip_per_problem_artifacts,
        )
        run_checked(cmd, repo_root, dry_run=args.dry_run)

    if phase in {"lean-commit", "promote-cache"} and not args.skip_final_artifacts:
        run_checked(["tools/index/gen_mltheory_index.sh"], repo_root, dry_run=args.dry_run)
        run_checked(["tools/index/gen_graph_artifacts.sh"], repo_root, dry_run=args.dry_run)

    if phase in {"lean-commit", "promote-cache", "proof-scope", "apply-replan"}:
        run_checked(
            ["python3", "tools/ci/check_problem_workspace_contract.py"],
            repo_root,
            dry_run=args.dry_run,
        )

    write_run_summary(suite_path=suite_path, phase=phase, problems=problems, dry_run=args.dry_run)
    print(f"[problem_suite] phase={phase} completed for {len(problems)} problems")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Problem Suite helper for Intake v2")
    sub = ap.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="create suites/<suite_id>/suite.yaml template")
    init.add_argument("--suite-id", required=True, help="suite identifier")
    init.add_argument("--repo-root", default=".", help="MLTheory repo root")
    init.add_argument("--force", action="store_true", help="overwrite existing suite template")

    run = sub.add_parser("run", help="run intake over all problems in a suite")
    run.add_argument("--suite", required=True, help="path to suite.yaml")
    run.add_argument(
        "--phase",
        required=True,
        choices=["research-pack", "lean-commit", "proof-scope", "stuck-batch", "apply-replan", "promote-cache"],
        help="intake phase to execute for all problems",
    )
    run.add_argument(
        "--batch-id",
        default="batch-001",
        help="batch id for stuck-batch/apply-replan phases",
    )
    run.add_argument("--repo-root", default=".", help="MLTheory repo root")
    run.add_argument("--skip-final-artifacts", action="store_true", help="skip final artifact refresh")
    run.add_argument("--dry-run", action="store_true", help="print commands without executing")
    return ap


def main() -> int:
    args = build_parser().parse_args()
    if args.cmd == "init":
        return cmd_init(args)
    return cmd_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
