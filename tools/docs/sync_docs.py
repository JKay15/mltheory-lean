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
GENERATED_NOTE = "<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->"
PARTIAL_REASON_EVIDENCE_TOKENS = (
    "external",
    "source_url",
    "candidate_repo",
    "github",
    "mathlib",
    "evidence",
    "证据",
    "候选",
    "来源",
)
PROMOTION_DECISION_RE = re.compile(
    r"`([^`]+)` 已从 planned_modules 提升为真实 file-backed module"
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
            "# 决策日志",
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
                backlog.get("priority", "—"),
                m["reason"],
            ]
        )
    return "\n".join(
        [
            "# 模块总表（Module Catalog）",
            "",
            GENERATED_NOTE,
            "",
            "## 真实模块（file-backed）字段约束：",
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
            "## 规划模块（non-file-backed）字段约束：",
            "- `module_path`",
            "- `target_node_id`",
            "- `source_track(native/books)`",
            "- `status(planned/partial/covered/gap)`",
            "- `execution_horizon(near/mid/far/unscheduled)`：来自 `execution_backlog`（未入短清单则为 unscheduled）",
            "- `execution_priority(P1/P2/P3)`：来自 `execution_backlog`（未入短清单则为 `—`）",
            "- `status=partial` 时，`reason` 必须包含可追溯证据（如 external/source_url/candidate_repo/证据）",
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
        evidence = "；".join(
            f"{node_name.get(n, n)}: real=0 planned={c}" for n, c in hollow_hotspots
        )
        issues.append(
            {
                "issue_id": "S1",
                "severity": "P1",
                "title": "主树空心节点（规划很多，真实模块为 0）",
                "evidence": evidence,
                "scope": f"{sum(c for _, c in hollow_hotspots)} 个规划模块",
                "action": "先给每个热点节点补 1 个 file-backed 骨架入口（非占位证明），再按书/主题逐步填充。",
                "acceptance_gate": "对应节点 real_modules >= 1；lake build + check_namespace_layout 通过。",
                "rollback_point": "仅新增骨架文件与 import；如不满意可回退该批新增文件与相应 import。",
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
                "title": "公开入口仍是 placeholder",
                "evidence": f"{len(public_placeholders)} 个：{names}",
                "scope": "applications 用户入口",
                "action": "把 placeholder 入口降级为 internal，或改成 bridge/compat 并明确指向可用 canonical 入口。",
                "acceptance_gate": "role=placeholder 且 user_surface=public 的真实模块数量为 0。",
                "rollback_point": "仅变更 registry 字段（role/user_surface）；可单次回滚 JSON 变更。",
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
                "title": "仍有 active alias，入口双轨并存",
                "evidence": f"active aliases={len(active_aliases)}；示例：{names}",
                "scope": "FoML2/SB2 章节兼容入口",
                "action": "为每条 active alias 增加退役批次与窗口，逐批切换到 deprecated 并执行防回流扫描。",
                "acceptance_gate": "active aliases 按批次单调下降，且 check_no_new_deprecated_imports 持续通过。",
                "rollback_point": "如迁移受阻，仅将受影响 alias 状态切回 active，不动 canonical 文件。",
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
                "title": "关键入口声明已在，但证明状态仍是 statement",
                "evidence": f"{len(statement_entries)} 个模块；示例：{names}",
                "scope": "canonical/tool 可信度",
                "action": "按 canonical_specs 优先级把 statement 入口逐批推进到 proved；先补依赖闭包最短链路。",
                "acceptance_gate": "canonical/tool 的 proved 比例按批次上升，且 canonical_contract 持续通过。",
                "rollback_point": "单批证明失败时只回滚该批 theorem 变更，不回滚已通过批次。",
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
                "title": "规划模块状态语义混杂（partial/gap 同时存在）",
                "evidence": (
                    f"planned status 分布：planned={planned_status.get('planned', 0)}，"
                    f"partial={planned_status.get('partial', 0)}，gap={planned_status.get('gap', 0)}；"
                    f"无证据 partial={len(partial_without_evidence)}（示例：{names}）"
                ),
                "scope": "路线图可读性",
                "action": "收敛 planned 状态语义：未落地文件优先用 planned/gap，partial 仅用于有明确外部可复用证据。",
                "acceptance_gate": "planned_modules 的 partial 条目有一致理由模板且可追溯来源。",
                "rollback_point": "仅调整 planned_modules.status/reason 文案，可单次回滚 registry。",
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
            "先把空心节点和公开 placeholder 收敛到可用入口（不改 theorem 语义）",
            "lake build + check_namespace_layout + check_placeholder_policy",
            "回滚新增骨架文件与 registry 字段改动",
        ],
        [
            "Phase-2",
            "S3",
            "active alias 分批退役，保证用户入口单轨化",
            "check_no_new_deprecated_imports + ImportSmoke",
            "把受阻 alias 从 deprecated 切回 active",
        ],
        [
            "Phase-3",
            "S4",
            "关键 canonical/tool 从 statement 推进到 proved",
            "check_canonical_contract + lake build",
            "仅回滚当前批 theorem，不影响已收敛批次",
        ],
        [
            "Phase-4",
            "S5",
            "整理 planned 状态语义，降低路线图歧义",
            "validate_ssot + sync_docs --check",
            "仅回滚 planned_modules 的状态与 reason 文案",
        ],
    ]
    phase_rows = []
    for phase, focus, goal, gates, rollback in phase_rows_raw:
        focus_ids = {x.strip() for x in focus.split("+")}
        status = "pending" if focus_ids & active_issue_ids else "done"
        phase_rows.append([phase, status, focus, goal, gates, rollback])

    return "\n".join(
        [
            "# 结构问题台账（Structure Issues）",
            "",
            GENERATED_NOTE,
            "",
            "## 这份文档解决什么问题（人话）",
            "1. 不靠主观印象，直接从当前 `registry.json` 统计结构问题。",
            "2. 每个问题都给证据、影响范围、下一步动作、验收门禁、回滚点。",
            "3. 目标是让“先修什么、怎么修、失败怎么退”一眼可见。",
            "",
            "## 当前自动识别的问题",
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
            "## 分批重整顺序（可回滚）",
            table(
                ["phase", "status", "focus_issues", "goal", "gates", "rollback"],
                phase_rows,
            ),
            "",
            "## 使用方式",
            "1. 先看最高 severity 的问题（若存在 `P1`，优先修 `P1`）。",
            "2. 每完成一批，都跑对应 gates；未过门禁不进入下一批。",
            "3. 若某批卡住，按该批 rollback 先撤回，再拆小批次重试。",
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
        "# 规划执行清单（Execution Backlog）",
        "",
        GENERATED_NOTE,
        "",
        "## 一眼看懂",
        f"- 规划模块总数：{len(registry['planned_modules'])}",
        f"- 执行短清单总数：{len(backlog)}",
        f"- 未排期（unscheduled）：{len(unscheduled)}",
        "- 解释：`near`=最近两轮就要推进，`mid`=后续阶段，`far`=远期探索。",
        "",
        "## near（近期）",
    ]

    near_rows = []
    for row in by_horizon["near"]:
        module_path = row["module_path"]
        target_node = planned_by_path.get(module_path, {}).get("target_node_id", "—")
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
    lines.extend(["", "## mid（中期）"])

    mid_rows = []
    for row in by_horizon["mid"]:
        module_path = row["module_path"]
        target_node = planned_by_path.get(module_path, {}).get("target_node_id", "—")
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
    lines.extend(["", "## far（远期）"])

    far_rows = []
    for row in by_horizon["far"]:
        module_path = row["module_path"]
        target_node = planned_by_path.get(module_path, {}).get("target_node_id", "—")
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
            "## 未排期模块（Top 25）",
            table(["module_path"], unscheduled_rows),
            "",
            "## 使用方式",
            "1. 每次只从 `near` 里取 1-2 项推进，避免并发过多导致质量下降。",
            "2. 只有完成 `done_when`，才允许把条目从 short-list 移出或降级到 `mid/far`。",
            "3. 新增规划模块时，优先决定是否进入 `execution_backlog`，否则默认 `unscheduled`。",
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
            recent_rows.append([module_path, "—", "—", "—", "—"])
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
        target = planned["target_node_id"] if planned else "—"
        backlog_rows.append(
            [
                row.get("horizon", "—"),
                row.get("priority", "—"),
                mpath,
                node_name.get(target, target),
                row.get("why_now", "—"),
                row.get("done_when", "—"),
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
        "# 验收看板（Review Dashboard）",
        "",
        GENERATED_NOTE,
        "",
        "## 你先看这四件事",
        f"1. 真实模块：`{len(modules)}`",
        f"2. 规划模块：`{len(planned_modules)}`",
        f"3. 当前短清单：`{len(backlog_rows)}`",
        f"4. 最近提升（planned -> file-backed）：`{len(recent_rows)}`",
        "",
        "## 最近提升（planned -> file-backed）",
        table(
            ["module_path", "node", "role", "proof_status", "先看声明(Top3)"],
            recent_rows if recent_rows else [["（暂无）", "—", "—", "—", "—"]],
        ),
        "",
        "## 当前执行焦点（execution_backlog）",
        table(
            ["horizon", "priority", "module_path", "target_node", "why_now", "done_when"],
            backlog_rows if backlog_rows else [["—", "—", "（空）", "—", "—", "—"]],
        ),
        "",
        "## 结构热区（按规划压力排序）",
        table(["node_name", "node_id", "real_modules", "planned_modules"], node_rows[:8]),
        "",
        "## 一键验收命令",
        "通过标准：以上命令全部 `PASS` / `Build completed successfully`。",
        "```bash",
        *gate_commands,
        "```",
        "",
        "## 怎么用（人话）",
        "1. 先看“最近提升”，判断这批是否是你想要的方向。",
        "2. 再看“当前执行焦点”，确认下一步是不是你认可的优先级。",
        "3. 最后复制“ 一键验收命令 ”跑完，确保这轮变更可独立复验。",
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
        "canonical": "主入口",
        "tool": "工具接口",
        "bridge": "桥接接口",
        "compat": "兼容入口",
        "placeholder": "占位入口",
    }
    layer_desc = {
        "core": "基础层",
        "methods": "方法层",
        "applications": "应用层",
        "books": "书籍层",
        "legacy": "兼容层",
    }

    lines = [
        "# 最小 API 卡片（APICards）",
        "",
        GENERATED_NOTE,
        "",
        "## 怎么用（2 分钟）",
        "1. 先看“最近变更优先看”，只检查这几项是否符合你的预期。",
        "2. 再到对应领域分组，按模块卡片看：做什么 + 先看哪些声明。",
        "3. 不需要一次看全库；每轮只抽查 3-5 个模块即可。",
        "",
        "## 最近变更优先看",
    ]

    recent_rows = []
    for module_path in _extract_recent_promotions(registry, limit=10):
        mod = next((m for m in modules if m["module_path"] == module_path), None)
        if mod is None:
            recent_rows.append([module_path, "—", "—", "—"])
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
            ["module_path", "node", "状态(layer/role/proof)", "先看声明(Top3)"],
            recent_rows if recent_rows else [["（暂无）", "—", "—", "—"]],
        )
    )
    lines.extend(["", "## 按领域查看（public 模块）"])

    for nid in [n["node_id"] for n in _taxonomy_nodes_sorted(registry)]:
        mods = sorted(by_node.get(nid, []), key=lambda m: m["module_path"])
        if not mods:
            continue
        nname = node_name.get(nid, nid)
        lines.append("")
        lines.append(f"### {nname}（{len(mods)}）")
        for m in mods:
            mark = "[NEW] " if m["module_path"] in recent_promotions else ""
            purpose = (
                f"{layer_desc.get(m['layer'], m['layer'])}的"
                f"{role_desc.get(m['role'], m['role'])}"
            )
            lines.append(
                (
                    f"- {mark}`{m['module_path']}`：{purpose}；"
                    f"先看 `{_decl_preview(m['formal_decl_refs'], limit=3)}`；"
                    f"状态 `{m['proof_status']}`；"
                    f"文件 `{_module_path_to_file(m['module_path'])}`"
                )
            )

    lines.extend(
        [
            "",
            "## 抽查建议",
            "1. 每次先抽查 1 个 `NEW` 模块 + 1 个同领域旧模块，确认风格是否一致。",
            "2. 若卡片描述与代码不一致，优先修 SSOT，再重新生成文档。",
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
        target = planned_by_path.get(mpath, {}).get("target_node_id", "—")
        backlog_rows.append(
            [
                row.get("horizon", "—"),
                row.get("priority", "—"),
                mpath,
                node_name.get(target, target),
                row.get("why_now", "—"),
                row.get("done_when", "—"),
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
                [decision_row.get("date", "—"), module_path, "—", "—", decision_row.get("impact", "—")]
            )
            continue
        promotion_rows.append(
            [
                decision_row.get("date", "—"),
                module_path,
                node_name.get(mod["primary_node_id"], mod["primary_node_id"]),
                f"{mod['layer']}/{mod['role']}/{mod['proof_status']}",
                decision_row.get("impact", "—"),
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
    audit_summary = "（未找到 lean4_contract_audit.json）"
    if isinstance(audit, dict):
        audit_summary = (
            f"date={audit.get('date', '—')}；mode={audit.get('mode', '—')}；"
            f"score={audit.get('score', '—')}；status={audit.get('status', '—')}"
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
                        row.get("check_id", "—"),
                        row.get("title", "—"),
                        "PASS" if row.get("passed") else "FAIL",
                        hit_count,
                    ]
                )

    lines = [
        "# GPT5.2pro 重构交接包（MLTheory 全量实现快照）",
        "",
        GENERATED_NOTE,
        "",
        "## 目的（给重构模型）",
        "1. 这份文档是“已做工作全量快照”，用于避免重构时丢上下文。",
        "2. 数据全部来自 `docs/ssot/registry.json`（和审查文件 `docs/ssot/lean4_contract_audit.json`）。",
        "3. 你可以把这份文档直接喂给 GPT5.2pro，让它基于真实现状更新重构方案。",
        "",
        "## 一眼看懂当前状态",
        f"- SSOT schema_version：`{registry['meta']['schema_version']}`",
        f"- last_updated：`{registry['meta']['last_updated']}`",
        f"- 决策总数：`{len(registry['decisions'])}`",
        f"- 真实模块（file-backed）总数：`{len(modules)}`",
        f"- 规划模块（non-file-backed）总数：`{len(planned_modules)}`",
        f"- 执行短清单（execution_backlog）条数：`{len(backlog_rows)}`",
        f"- aliases 总数：`{len(registry['aliases'])}`",
        f"- gaps 总数：`{len(registry['gaps'])}`",
        "",
        "## 当前下一步（短清单）",
        table(
            ["horizon", "priority", "module_path", "target_node", "why_now", "done_when"],
            backlog_rows if backlog_rows else [["—", "—", "（空）", "—", "—", "—"]],
        ),
        "",
        "## 架构契约（重构时默认不可破）",
        "### 1) taxonomy 主树",
        table(
            ["node_id", "name", "tier", "primary_parent_id", "status", "order"],
            taxonomy_rows,
        ),
        "",
        "### 2) taxonomy 关系边（secondary_parent/related）",
        table(
            ["from_node", "from_name", "to_node", "to_name", "relation_type", "strength"],
            relation_rows if relation_rows else [["—", "—", "—", "—", "—", "—"]],
        ),
        "",
        "### 3) 官方工作流对齐（Lean 官方资源映射）",
        table(
            ["capability", "source_url", "status", "local_enforcement"],
            workflow_rows,
        ),
        "",
        "### 4) canonical spec 契约",
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
        "## Phase-0 / skill 对齐审查快照",
        f"- {audit_summary}",
        table(
            ["#", "check_id", "title", "result", "hits"],
            audit_rows if audit_rows else [["—", "—", "—", "—", "—"]],
        ),
        "",
        "## 已完成实现（planned -> file-backed 提升轨迹）",
        table(
            ["date", "module_path", "node", "state(layer/role/proof)", "impact"],
            promotion_rows if promotion_rows else [["—", "—", "—", "—", "—"]],
        ),
        "",
        "## 真实模块全量清单（实现细节）",
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
        "## 规划模块全量清单（未落地）",
        table(
            ["module_path", "target_node", "source_track", "status", "reason"],
            planned_rows,
        ),
        "",
        "## 结构风险与重构优先级（自动识别）",
        table(
            ["issue_id", "severity", "title", "evidence", "action", "acceptance_gate"],
            issue_rows if issue_rows else [["—", "—", "（无）", "—", "—", "—"]],
        ),
        "",
        "## 可复现验收命令（重构后至少跑这些）",
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
        "## 给 GPT5.2pro 的建议阅读顺序",
        "1. 先看“架构契约”与“Phase-0 审查快照”，确认硬约束。",
        "2. 再看“已完成实现轨迹”与“真实模块全量清单”，避免重复造轮子。",
        "3. 最后看“规划模块全量清单 + 结构风险”，决定推翻重做范围与迁移策略。",
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
        return "—"
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
    taxonomy_nodes = _taxonomy_nodes_sorted(registry)
    node_name = _node_name_map(registry)
    real_rows, planned_rows = _build_forest_rows(registry)
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
        [r["from_node"], node_name.get(r["from_node"], r["from_node"]), r["to_node"], node_name.get(r["to_node"], r["to_node"]), r["relation_type"], r["strength"]]
        for r in registry["taxonomy_relations"]
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
            r["execution_priority"] or "—",
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
        target_node = planned_by_path.get(module_path, {}).get("target_node_id", "—")
        backlog_rows.append(
            [
                row.get("horizon", "—"),
                row.get("priority", "—"),
                module_path,
                node_name.get(target_node, target_node),
                _short_text(str(row.get("why_now", "—")), limit=56),
                _short_text(str(row.get("done_when", "—")), limit=56),
            ]
        )

    lines = [
        "# 工具森林（Tool Forest）",
        "",
        GENERATED_NOTE,
        "",
        "## 一眼看懂",
        f"- 真实模块数：{len(real_rows)}",
        f"- 规划模块数：{len(planned_rows)}",
        f"- 规划执行短清单：{backlog_count}",
        f"- 规划未排期：{unscheduled_count}",
        f"- taxonomy 节点数：{len(taxonomy_nodes)}",
        (
            f"- 真实模块角色：canonical={role_count['canonical']}，tool={role_count['tool']}，"
            f"compat={role_count['compat']}，bridge={role_count['bridge']}，placeholder={role_count['placeholder']}"
        ),
        (
            f"- 真实模块证明状态：proved={proof_count['proved']}，statement={proof_count['statement']}，"
            f"placeholder={proof_count['placeholder']}"
        ),
        "- `Books/Legacy` 已改为 `source_track` 轴，不再作为主树节点。",
        "",
        "## 视图 A：Taxonomy 主树",
        *view_a,
        "",
        "## 表 1：taxonomy 节点总览",
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
        "## 表 2：关系边（次父/关联）",
        table(
            ["from_node", "from_name", "to_node", "to_name", "relation_type", "strength"],
            relation_rows,
        ),
        "",
        "## 表 3：source_track 分布（真实/规划）",
        table(
            ["source_track", "real_modules", "planned_modules"],
            source_rows,
        ),
        "",
        "## 表 4：入口模块（canonical + tool，Top 20）",
        f"- 全量入口数：{len(entry_rows_all)}（这里默认只展示前 20 条，详细请看交互页）",
        table(
            ["module_path", "node_name", "source_track", "layer", "role", "proof_status", "formal_decl_refs"],
            entry_rows,
        ),
        "",
        "## 表 5：规划模块样例（Top 12）",
        f"- 全量规划模块数：{len(planned_top_rows_all)}（这里只展示前 12 条，避免刷屏）",
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
        "## 表 6：规划执行短清单（near/mid/far）",
        table(
            ["horizon", "priority", "module_path", "target_node", "why_now", "done_when"],
            backlog_rows[:10],
        ),
        "",
        "## 交互页（完整明细）",
        "- 见 [ToolForestInteractive.html](./ToolForestInteractive.html)。",
        "- 默认只显示 `真实模块`；需要时再切到 `规划模块`。",
        "- 支持 `真实模块/规划模块` 开关、node/source/layer/role/proof/plan window 筛选与搜索。",
        "- 想快速验收本轮变化：看 [ReviewDashboard.md](./ReviewDashboard.md)。",
        "- 想快速理解模块用途：看 [APICards.md](./APICards.md)。",
        "",
        "## 使用说明（人 + Codex）",
        "1. 本文档由 `docs/ssot/registry.json` 自动生成，禁止手改。",
        "2. 主树看 `taxonomy_nodes`，横向关系看 `taxonomy_relations`。",
        "3. 真实结构看 `modules`；路线图看 `planned_modules`。",
        "4. 变更流程：",
        "- 先改 `docs/ssot/registry.json`。",
        "- 跑 `python3 tools/docs/validate_ssot.py`。",
        "- 跑 `python3 tools/docs/sync_docs.py --write`。",
        "- 跑 `python3 tools/ci/check_taxonomy_contract.py`。",
        "- 跑 `python3 tools/ci/check_tool_forest_consistency.py`。",
        "",
    ]
    return "\n".join(lines)


def render_tool_forest_interactive(registry: dict) -> str:
    nodes = _taxonomy_nodes_sorted(registry)
    relations = registry["taxonomy_relations"]
    real_rows, planned_rows = _build_forest_rows(registry)
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
        这个页面只读 `docs/ssot/registry.json` 派生数据。<br />
        默认先看真实模块；只有需要排期时再切到规划模块视图。
      </div>
      <div class="chips" id="summary"></div>
    </div>

    <div class="card controls">
      <div>
        <label for="q">搜索</label>
        <input id="q" placeholder="module/node/subdomain/key_problem/formal decl" />
      </div>
      <div>
        <label for="f-dataset">Dataset</label>
        <select id="f-dataset">
          <option value="">全部</option>
          <option value="real" selected>真实模块</option>
          <option value="planned">规划模块</option>
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
        <button id="reset">重置筛选</button>
      </div>
    </div>

    <div class="card">
      <div class="muted" style="margin-bottom:6px;">快速视图</div>
      <div class="chips">
        <button class="qbtn" id="preset-real">只看真实模块</button>
        <button class="qbtn" id="preset-near">只看近期规划</button>
        <button class="qbtn" id="preset-all">显示全部</button>
      </div>
    </div>

    <div class="layout">
      <div class="card">
        <div class="muted" style="margin-bottom:8px;">领域结构（可折叠）</div>
        <div class="tree" id="tree"></div>
      </div>
      <div class="card">
        <div class="muted" style="margin-bottom:8px;">模块列表（点击行看详情）</div>
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
          <div class="muted">点击上方任意模块行显示详情。</div>
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
      opt0.textContent = "全部";
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
        tr.innerHTML = `<td colspan="7" class="muted">已显示前 ${MAX_ROWS} 条，共 ${list.length} 条。请继续筛选或搜索。</td>`;
        dom.tbody.appendChild(tr);
      }}
    }}

    function renderDetail(m) {{
      dom.detail.innerHTML = `
        <div class="k">module_path</div><div class="v">${m.module_path}</div>
        <div class="k">node / subdomain / key_problem</div><div class="v">${m.node_name} / ${m.subdomain} / ${m.key_problem}</div>
        <div class="k">dataset / source_track</div><div class="v">${m.dataset} / ${m.source_track}</div>
        <div class="k">plan window / priority / shortlist</div><div class="v">${m.execution_horizon || "—"} / ${m.execution_priority || "—"} / ${m.in_backlog ? "yes" : "no"}</div>
        <div class="k">layer / role / proof_status</div><div class="v">${m.layer} / ${m.role} / ${m.proof_status}</div>
        <div class="k">formal_decl_refs</div><div class="v">${(m.formal_decl_refs || []).join(", ") || "—"}</div>
        <div class="k">status</div><div class="v">${m.status || "—"}</div>
        <div class="k">reason</div><div class="v">${m.reason || "—"}</div>
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
            "1. 本清单用于结构重整排期，不在本轮执行物理删除。",
            "2. 每条候选都必须给证据：定义文件 + 被 import 位置。",
            "3. `execution_state`：`pending` -> `deprecated_announced` -> `migrating` -> `ready_to_remove`。",
            "4. `remove_after_releases` + `migration_started_epoch` + `meta.cleanup_release_epoch` 决定是否到期可删。",
            "5. 本清单先执行 `deprecated`，兼容窗口结束后再评估物理删除。",
            "6. 真删前必须先写 `DecisionLog`，并跑全量门禁。",
        ]
    else:
        intro_lines = [
            "1. 当前 `structure_cleanup_candidates=0`，兼容入口分批删除已完成。",
            "2. 若后续新增兼容入口，必须先登记候选证据，再进入 `deprecated -> ready_to_remove -> physical remove` 流程。",
            "3. 删除动作仍要求先写 `DecisionLog`，并跑全量门禁。",
        ]

    return "\n".join(
        [
            "# 结构清理候选（只做清单）",
            "",
            GENERATED_NOTE,
            "",
            "## 说明",
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
                "<br>".join(examples) if examples else "—",
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
        "当前 `structure_cleanup_candidates = 0`，兼容入口分批删除已完成。"
        if not cleanup
        else f"当前仍有 {len(cleanup)} 条 cleanup 候选，详见 `StructureCleanupCandidates.md`。"
    )

    return "\n".join(
        [
            "# 命名空间收敛视图（Namespace Convergence）",
            "",
            GENERATED_NOTE,
            "",
            "## 目标（人话）",
            "1. 新模块必须落在分层前缀下（`Core/Methods/Applications/Books`）。",
            "2. `legacy` 层仅保留顶层兼容入口（`MLTheory.X`），不再新增深层 legacy 路径。",
            "3. 旧入口统一通过 `aliases` 映射到新入口，避免“看起来还能 import，但不知道该改到哪里”。",
            "",
            "## 当前收敛状态",
            f"- {cleanup_summary}",
            f"- 真实模块总数：{len(modules)}",
            f"- alias 总数：{len(aliases)}（deprecated={len(deprecated_alias_rows)} / active={len(active_alias_rows)}）",
            "",
            "## 分层前缀约束（真实模块）",
            table(["layer", "required_prefix", "module_count", "examples"], prefix_rows),
            "",
            "## 剩余顶层 legacy 入口（保留兼容）",
            table(
                ["module_path", "source_track", "role", "status", "proof_status"],
                legacy_root_rows,
            ),
            "",
            "## Deprecated Alias（旧入口 -> 新入口）",
            table(["legacy_module", "canonical_module", "status"], deprecated_alias_rows),
            "",
            "## Active Alias（仍处于兼容映射）",
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
            "# 全局缺口台账（Gap Ledger）",
            "",
            GENERATED_NOTE,
            "",
            "字段约束：`book`、`chapter`、`topic`、`status`、`last_search_date`、`sources_checked`、`candidate_repo`、`next_action`",
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
    lines = []
    lines.append(f"# {book['title']} 覆盖映射")
    lines.append("")
    lines.append(GENERATED_NOTE)
    lines.append("")
    lines.append("## 书目信息")
    lines.append(f"- 书名：{book['title']}")
    lines.append(f"- 版本：{book['edition']}")
    lines.append(f"- 覆盖日期：{last_updated}")
    lines.append("- 维护人：Codex + 用户")
    lines.append("")
    lines.append("## 目录来源与证据")
    if book["evidence_links"]:
        for i, link in enumerate(book["evidence_links"], start=1):
            lines.append(f"{i}. `{link}`")
    else:
        lines.append("1. （暂无外部 URL；见对应章节的证据描述）")
    lines.append("")
    lines.append("## 章节覆盖表（SSOT 派生）")
    rows = [
        [
            r["章节"],
            r["对应模块"],
            r["覆盖状态"],
            r["证据链接"],
            r["缺口说明"],
            r["后续动作"],
        ]
        for r in book["coverage_rows"]
    ]
    lines.append(
        table(
            ["章节", "对应模块", "覆盖状态", "证据链接", "缺口说明", "后续动作"],
            rows,
        )
    )
    lines.append("")
    lines.append("## 与全局文档联动")
    lines.append("1. 模块路径以 `../ModuleCatalog.md` 为唯一模块清单来源。")
    lines.append("2. 缺口追踪以 `../GapLedger.md` 为唯一缺口台账来源。")
    lines.append("3. 本文件仅保留章节覆盖映射，不重复维护全量模块表。")
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
                f"[../GapLedger.md](../GapLedger.md)（`book={book['book_id']}`）",
            ]
        )

    return "\n".join(
        [
            "# 书籍覆盖索引",
            "",
            GENERATED_NOTE,
            "",
            "## 覆盖文档",
            table(["书籍", "覆盖文档", "缺口来源"], rows),
            "",
            "## 模板",
            "- [下一本书覆盖模板](./_BookCoverageTemplate.md)",
            "",
            "## 使用约定",
            "1. 每本书先落覆盖文档，再补缺口条目。",
            "2. 覆盖状态只用三档：`covered`、`partial`、`gap`（允许 `planned` 仅用于尚未落位章节）。",
            "3. 文档里的模块名必须与 `../ModuleCatalog.md` 的 `module_path` 一致。",
            "",
        ]
    )


def render_glossary() -> str:
    return "\n".join(
        [
            "# 术语白话表（Glossary）",
            "",
            GENERATED_NOTE,
            "",
            "## 数据结构基础",
            "1. JSON：一种数据格式，可表达对象（键值对）和数组（列表）。",
            "2. root（最外层）：JSON 文件最外面那层对象。",
            "3. 对象（object）：形如 `{ \"键\": 值 }`。",
            "4. 数组（array）：形如 `[值1, 值2, ...]`。",
            "",
            "## SSOT 根字段（`docs/ssot/registry.json`）",
            "1. `meta`：项目全局信息（语言、toolchain、更新时间、策略、cleanup_release_epoch）。",
            "2. `decisions`：决策日志（日期、决策、状态、影响）。",
            "3. `taxonomy_nodes`：主树节点（主父关系 + tier 标签）。",
            "4. `taxonomy_relations`：横向关系边（次父/关联 + 强度 0~1）。",
            "5. `official_workflow_refs`：Lean 官方工作流能力与本仓落地点映射。",
            "6. `canonical_specs`：canonical 入口契约（签名/禁词/依赖闭包）。",
            "7. `modules`：真实模块清单（必须有本地 `.lean` 文件）。",
            "8. `planned_modules`：规划模块清单（允许暂未落地文件）。",
            "9. `execution_backlog`：规划短清单（`near/mid/far` + 优先级 + 完成定义）。",
            "10. `structure_cleanup_candidates`：结构重整候选（执行状态、分批、兼容窗口、窗口数值、迁移起点、替代入口、风险、建议动作）。",
            "11. `gaps`：缺口台账（没覆盖或部分覆盖的主题与后续动作）。",
            "12. `books`：书籍覆盖映射（章节 -> 模块 -> 覆盖状态）。",
            "13. `aliases`：兼容映射（旧模块路径 -> 新模块路径）。",
            "",
            "## 模块相关术语",
            "1. 模块（module）：一个可被 `import` 的 Lean 代码单元，通常对应一个 `.lean` 文件。",
            "2. `module_path`：模块路径，如 `MLTheory.Core.Learning.PAC`。",
            "3. `status`：覆盖状态，`planned/partial/covered/gap`。",
            "3.1 对 `planned_modules`，`partial` 只允许用于“有可追溯外部证据”的条目；否则应使用 `planned` 或 `gap`。",
            "4. `primary_node_id`：模块在 taxonomy 主树中的主归属节点。",
            "5. `source_track`：来源轴（`native/books/legacy`）。",
            "5.1 在 `modules` 中可取 `native/books/legacy`；在 `planned_modules` 中只允许 `native/books`。",
            "5.2 `execution_backlog` 用于给 `planned_modules` 做短队列排期：`near`（近期）、`mid`（中期）、`far`（远期）。",
            "6. `layer`：分层归属，`core/methods/applications/books/legacy`。",
            "7. `proof_status`：证明进度，`placeholder/statement/proved`。",
            "8. `placeholder_policy_scope`：占位策略，`allowed/forbidden`。",
            "9. `role`：模块角色（canonical/compat/bridge/tool/placeholder）。",
            "10. `user_surface`：对使用者是否作为公开入口（public/internal）。",
            "11. `formal_decl_refs`：该模块承载的关键声明名清单。",
            "",
            "## 文档生成与一致性",
            "1. SSOT（Single Source of Truth）：单一事实源，这里是 `docs/ssot/registry.json`。",
            "2. 派生文档：从 SSOT 自动生成的 Markdown（如 `INDEX.md`、`ModuleCatalog.md`）。",
            "3. `sync_docs.py --write`：按固定模板生成文档。",
            "4. `sync_docs.py --check`：重新生成一份“期望文本”，与当前文件逐字比较；任一不同就报错。",
            "5. 固定模板：`tools/docs/sync_docs.py` 里的 `render_*` 函数（标题、列顺序、说明文字都写死）。",
            "6. `NamespaceConvergence.md`：命名空间收敛视图（也是 SSOT 派生，不允许手改）。",
            "",
            "## Lean 构建与检查",
            "1. `lake build`：构建整个 Lean 项目（解析 import、类型检查、生成产物）。",
            "2. `import`：导入模块。",
            "3. `#check`：检查某个名字是否存在、类型是否正确。",
            "4. 冒烟检查（smoke）：用最小例子快速确认关键路径仍可编译。",
            "",
            "## 质量门禁脚本",
            "1. `check_no_sorry_axiom.sh`：扫描是否出现 `sorry` 或 `axiom`。",
            "2. `sorry`：临时占位，表示证明未完成但先让编译通过。",
            "3. `axiom`：直接引入未证明前提，会降低形式化可靠性。",
            "4. `check_placeholder_policy.sh`：检查 `Core/Methods` 不允许 `Prop := True` 占位，并核对 SSOT 占位策略字段。",
            "5. 占位允许范围：当前策略允许 `applications/books/legacy` 保留阶段性占位，不允许 `core/methods` 占位回归。",
            "6. `check_canonical_contract.sh`：检查 canonical 契约声明存在性、禁词与依赖引用。",
            "7. `check_official_workflow_alignment.sh`：检查官方能力映射（Loogle/LeanSearch/InfoView/LoogleView/REPL）。",
            "8. `check_tool_forest_consistency.py`：检查概念树与模块归属一致性。",
            "9. `check_review_views_consistency.py`：检查 ReviewDashboard/APICards/交互页默认行为是否与 SSOT 一致。",
            "10. `check_namespace_layout.py`：检查模块路径是否遵守分层前缀与 alias 收敛约束。",
            "11. `check_no_new_deprecated_imports.sh`：禁止新增对已弃用兼容入口的 import（防回流）。",
            "12. `check_ready_to_remove.py`：按 release 窗口自动判定是否应进入 `ready_to_remove`。",
            "13. `check_registry_reference_hygiene.py`：检查 books/gaps 是否引用 deprecated alias，并检查 coverage 行是否出现重复模块。",
            "14. `check_ssot_migration_idempotent.sh`：检查迁移脚本幂等性（当前 registry 运行迁移后不得产生 diff）。",
            "15. `advance_cleanup_release_epoch.py`：推进 cleanup_release_epoch 并自动切换到期候选状态。",
            "16. `StructureCleanupCandidates.md`：结构重整候选清单（本轮只清单，不删文件）。",
            "",
            "## 兼容层与导入回归",
            "1. 兼容层：旧模块路径的薄封装文件，用于保持历史 `import` 不断。",
            "2. 薄封装：文件本身不承载核心实现，主要转发到新分层模块。",
            "3. 导入回归：`Eval/ImportSmoke.lean` 同时导入新路径和旧路径，验证重构后接口未断。",
            "",
            "## 开发环境术语",
            "1. symlink（符号链接）：类似快捷方式，指向另一个目录或文件。",
            "2. submodule（Git 子模块）：在一个仓库中固定引用另一个仓库的某个提交。",
            "3. MCP：Codex 使用的工具服务接入层；本项目用 `lean-lsp-mcp` 提供 Lean 交互能力。",
            "",
            "## 常用命令（本仓）",
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
            "## 常见报错（含义 -> 建议命令）",
            "| 报错片段 | 含义（白话） | 先跑哪个命令 |",
            "|---|---|---|",
            "| `Derived docs are out of sync` | 生成后的文档和仓库里现有文档不一致 | `python3 tools/docs/sync_docs.py --write` 然后 `--check` |",
            "| `missing keys` / `extra keys` | `registry.json` 字段不符合契约 | `python3 tools/docs/validate_ssot.py` 定位后修复 JSON 字段 |",
            "| `bad import` | 导入路径无效或依赖没拉到本地 | 先 `~/.elan/bin/lake build`，再检查对应 `import` 路径是否存在 |",
            "| `found forbidden token` | 出现了被禁止的 `sorry/axiom` | `tools/ci/check_no_sorry_axiom.sh` 定位并删除 |",
            "| `Prop := True placeholders` | `Core/Methods` 出现不允许的占位 | `tools/ci/check_placeholder_policy.sh` 定位并改为真实 statement |",
            "| `no such file or directory`（mathlib） | 依赖目录或路径不匹配 | `~/.elan/bin/lake build` 重新解析依赖并看首个失败点 |",
            "",
            "## 术语反查（看到新词时怎么找定义）",
            "1. 先在 `docs/Glossary.md` 看白话定义。",
            "2. 再在 `docs/ssot/registry.json` 查该词对应的字段或模块路径。",
            "3. 若是模块名（如 `MLTheory.X.Y`），用 `rg \"MLTheory\\.X\\.Y\" docs /Users/xiongjiangkai/xjk_papers/MLTheory/MLTheory` 找来源与引用。",
            "4. 若是脚本术语（如 `placeholder_policy_scope`），用 `rg \"placeholder_policy_scope\" /Users/xiongjiangkai/xjk_papers/MLTheory/tools` 找校验逻辑。",
            "5. 若是 CI 术语（如 `ImportSmoke`），看 `/Users/xiongjiangkai/xjk_papers/MLTheory/.github/workflows/lean_action_ci.yml` 对应步骤。",
            "6. 仍不清楚时，优先问“这个词在哪个文件第几行生效”，避免语义歧义。",
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
            "# MLTheory 文档索引",
            "",
            GENERATED_NOTE,
            "",
            "## 目的",
            "本目录用于沉淀 MLTheory 的历史决策、模块规划、书籍覆盖情况与缺口检索台账。",
            "",
            "## 核心导航",
            table(
                ["文档", "说明"],
                [
                    ["[../AGENTS.md](../AGENTS.md)", "代理执行规范（文档系统优先、删除留痕规则）"],
                    ["[DecisionLog.md](./DecisionLog.md)", "决策日志（固定字段：`date/decision/status/impact`）"],
                    ["[ModuleCatalog.md](./ModuleCatalog.md)", "模块总表（固定字段：`module_path/primary_node_id/source_track/status/...`）"],
                    ["[GapLedger.md](./GapLedger.md)", "全局缺口台账（固定字段：`book/chapter/topic/status/last_search_date/sources_checked/candidate_repo/next_action`）"],
                    ["[ToolForest.md](./ToolForest.md)", "概念 + 模块森林图（由 SSOT 自动生成）"],
                    ["[ToolForestInteractive.html](./ToolForestInteractive.html)", "可筛选/可搜索/可折叠的交互式结构视图（推荐日常使用）"],
                    ["[ReviewDashboard.md](./ReviewDashboard.md)", "验收看板（本轮新增、当前焦点、一键验收命令）"],
                    ["[RefactorHandoffForGPT52Pro.md](./RefactorHandoffForGPT52Pro.md)", "给 GPT5.2pro 的重构交接包（实现全景 + 门禁 + 风险）"],
                    ["[APICards.md](./APICards.md)", "最小 API 卡片（每个 public 模块做什么、先看哪些声明）"],
                    ["[ExecutionBacklog.md](./ExecutionBacklog.md)", "规划模块短清单（near/mid/far），把 96 条路线图收敛成可执行队列"],
                    ["[NamespaceConvergence.md](./NamespaceConvergence.md)", "命名空间收敛视图（层级前缀、legacy 入口、alias 映射）"],
                    ["[StructureIssues.md](./StructureIssues.md)", "结构问题台账（自动识别问题 + 分批整改顺序 + 回滚点）"],
                    ["[StructureCleanupCandidates.md](./StructureCleanupCandidates.md)", "结构重整候选清单（分批/窗口/替代入口/风险）"],
                    ["[books/README.md](./books/README.md)", "书籍覆盖索引页"],
                    ["[Glossary.md](./Glossary.md)", "术语白话表（减少黑话沟通成本）"],
                    ["[ssot/registry.json](./ssot/registry.json)", "单一事实源（唯一可手改数据文件）"],
                    ["[ssot/schema.json](./ssot/schema.json)", "SSOT 字段契约"],
                ],
            ),
            "",
            "## 书籍覆盖文档",
            table(["书籍", "覆盖文档"], book_rows),
            "",
            "## 维护规则（新增一本书时）",
            "1. 先更新 `ssot/registry.json`，再运行文档生成脚本。",
            "2. 执行 `python3 tools/docs/validate_ssot.py` 校验字段契约。",
            "3. 执行 `python3 tools/docs/sync_docs.py --write` 生成派生文档。",
            "4. 若有删除或替代，必须在 `DecisionLog.md` 留痕。",
            "",
            "## ToolForest 快速上手",
            "1. 验收当前一轮改动：先看 [ReviewDashboard.md](./ReviewDashboard.md)。",
            "2. 要给重构模型完整上下文：看 [RefactorHandoffForGPT52Pro.md](./RefactorHandoffForGPT52Pro.md)。",
            "3. 看模块用途与入口声明：再看 [APICards.md](./APICards.md)。",
            "3. 看整体结构：打开 [ToolForestInteractive.html](./ToolForestInteractive.html)（默认只看真实模块）。",
            "4. 要总览主树：看 [ToolForest.md](./ToolForest.md) 的“表 1：taxonomy 节点总览”。",
            "5. 要看近期排期：看 [ExecutionBacklog.md](./ExecutionBacklog.md)。",
            "6. 要看命名空间迁移路径：看 [NamespaceConvergence.md](./NamespaceConvergence.md)。",
            "7. 要看结构问题与清理候选：看 [StructureIssues.md](./StructureIssues.md) + [StructureCleanupCandidates.md](./StructureCleanupCandidates.md)。",
            "8. 任何结构调整都只能改 `ssot/registry.json`，再执行：",
            "- `python3 tools/docs/validate_ssot.py`",
            "- `python3 tools/docs/sync_docs.py --write`",
            "- `python3 tools/ci/check_taxonomy_contract.py`",
            "- `python3 tools/ci/check_tool_forest_consistency.py`",
            "- `python3 tools/ci/check_review_views_consistency.py`",
            "- `python3 tools/ci/check_namespace_layout.py`",
            "- `tools/ci/check_ssot_migration_idempotent.sh`",
            "- `tools/ci/check_no_new_deprecated_imports.sh`",
            "- `python3 tools/ci/check_ready_to_remove.py`",
            "- `python3 tools/ci/check_registry_reference_hygiene.py`",
            "",
            "## 当前默认约束",
            "1. 文档语言：中文。",
            "2. 文档组织：多文档索引制（不合并为单一总文档）。",
            "3. 近期策略：先稳固 SSOT 与分层模块骨架，再逐章补证明。",
            "4. 删除规则：不允许随意删除；有理由删除必须记录影响范围。",
            "",
        ]
    )


def render_book_template() -> str:
    return "\n".join(
        [
            "# 书籍覆盖模板（复制后重命名）",
            "",
            GENERATED_NOTE,
            "",
            "## 书目信息",
            "- 书名：",
            "- 版本：",
            "- 覆盖日期：",
            "- 维护人：",
            "",
            "## 章节覆盖表",
            "| 章节 | 对应模块 | 覆盖状态 | 证据链接 | 缺口说明 | 后续动作 |",
            "|---|---|---|---|---|---|",
            "| 示例：Ch1 | `MLTheory.XXX.YYY` | partial | `https://...` | 缺少某定理 | 在某模块新增占位并继续检索 |",
            "",
            "## 覆盖状态定义",
            "- `covered`：已有可直接复用的 Lean 形式化内容。",
            "- `partial`：有基础设施或外部候选，但未完整覆盖该章节。",
            "- `gap`：当前无可复用形式化实现。",
            "",
            "## 与全局文档联动",
            "1. 新增本书文档后，必须更新：",
            "- `../README.md`（书籍索引）",
            "- `../../ModuleCatalog.md`（`book_refs`）",
            "- `../../GapLedger.md`（缺口条目）",
            "- `../../DecisionLog.md`（关键策略变更）",
            "",
            "2. 记录粒度要求：",
            "- 每条 gap 必填 `last_search_date` 与 `next_action`。",
            "- 模块名必须与 `ModuleCatalog.md` 的 `module_path` 完全一致。",
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

    return files


def check_mode(outputs: dict[Path, str]) -> int:
    mismatches: list[Path] = []
    for path, content in outputs.items():
        if not path.exists():
            mismatches.append(path)
            continue
        current = path.read_text(encoding="utf-8")
        if current != content:
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
