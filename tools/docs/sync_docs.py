#!/usr/bin/env python3
"""Generate Markdown docs from docs/ssot/registry.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "ssot" / "registry.json"
GENERATED_NOTE = "<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->"


def load_registry() -> dict:
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing registry: {REGISTRY_PATH}")


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
    modules = sorted(registry["modules"], key=lambda m: m["module_path"])
    rows = [
        [
            m["module_path"],
            m["domain"],
            m["status"],
            m["source"],
            m["book_refs"],
            m["layer"],
            m["proof_status"],
            m["placeholder_policy_scope"],
        ]
        for m in modules
    ]
    return "\n".join(
        [
            "# 模块总表（Module Catalog）",
            "",
            GENERATED_NOTE,
            "",
            "字段约束：",
            "- `module_path`",
            "- `domain`",
            "- `status(planned/partial/covered/gap)`",
            "- `source(mathlib/slt/external)`",
            "- `book_refs`",
            "- `layer(core/methods/applications/books/legacy)`",
            "- `proof_status(placeholder/statement/proved)`",
            "- `placeholder_policy_scope(allowed/forbidden)`",
            "",
            table(
                [
                    "module_path",
                    "domain",
                    "status(planned/partial/covered/gap)",
                    "source(mathlib/slt/external)",
                    "book_refs",
                    "layer(core/methods/applications/books/legacy)",
                    "proof_status(placeholder/statement/proved)",
                    "placeholder_policy_scope(allowed/forbidden)",
                ],
                rows,
            ),
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
            "1. `meta`：项目全局信息（语言、toolchain、更新时间、策略）。",
            "2. `decisions`：决策日志（日期、决策、状态、影响）。",
            "3. `modules`：模块清单（每行描述一个 Lean 模块）。",
            "4. `gaps`：缺口台账（没覆盖或部分覆盖的主题与后续动作）。",
            "5. `books`：书籍覆盖映射（章节 -> 模块 -> 覆盖状态）。",
            "6. `aliases`：兼容映射（旧模块路径 -> 新模块路径）。",
            "",
            "## 模块相关术语",
            "1. 模块（module）：一个可被 `import` 的 Lean 代码单元，通常对应一个 `.lean` 文件。",
            "2. `module_path`：模块路径，如 `MLTheory.Core.Learning.PAC`。",
            "3. `status`：覆盖状态，`planned/partial/covered/gap`。",
            "4. `layer`：分层归属，`core/methods/applications/books/legacy`。",
            "5. `proof_status`：证明进度，`placeholder/statement/proved`。",
            "6. `placeholder_policy_scope`：占位策略，`allowed/forbidden`。",
            "",
            "## 文档生成与一致性",
            "1. SSOT（Single Source of Truth）：单一事实源，这里是 `docs/ssot/registry.json`。",
            "2. 派生文档：从 SSOT 自动生成的 Markdown（如 `INDEX.md`、`ModuleCatalog.md`）。",
            "3. `sync_docs.py --write`：按固定模板生成文档。",
            "4. `sync_docs.py --check`：重新生成一份“期望文本”，与当前文件逐字比较；任一不同就报错。",
            "5. 固定模板：`tools/docs/sync_docs.py` 里的 `render_*` 函数（标题、列顺序、说明文字都写死）。",
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
            "6. `~/.elan/bin/lake env lean Eval/ImportSmoke.lean`",
            "7. `~/.elan/bin/lake build`",
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
                    ["[ModuleCatalog.md](./ModuleCatalog.md)", "模块总表（固定字段：`module_path/domain/status/source/book_refs`）"],
                    ["[GapLedger.md](./GapLedger.md)", "全局缺口台账（固定字段：`book/chapter/topic/status/last_search_date/sources_checked/candidate_repo/next_action`）"],
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
