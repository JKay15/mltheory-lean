# 术语白话表（Glossary）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 数据结构基础
1. JSON：一种数据格式，可表达对象（键值对）和数组（列表）。
2. root（最外层）：JSON 文件最外面那层对象。
3. 对象（object）：形如 `{ "键": 值 }`。
4. 数组（array）：形如 `[值1, 值2, ...]`。

## SSOT 根字段（`docs/ssot/registry.json`）
1. `meta`：项目全局信息（语言、toolchain、更新时间、策略）。
2. `decisions`：决策日志（日期、决策、状态、影响）。
3. `modules`：模块清单（每行描述一个 Lean 模块）。
4. `gaps`：缺口台账（没覆盖或部分覆盖的主题与后续动作）。
5. `books`：书籍覆盖映射（章节 -> 模块 -> 覆盖状态）。
6. `aliases`：兼容映射（旧模块路径 -> 新模块路径）。

## 模块相关术语
1. 模块（module）：一个可被 `import` 的 Lean 代码单元，通常对应一个 `.lean` 文件。
2. `module_path`：模块路径，如 `MLTheory.Core.Learning.PAC`。
3. `status`：覆盖状态，`planned/partial/covered/gap`。
4. `layer`：分层归属，`core/methods/applications/books/legacy`。
5. `proof_status`：证明进度，`placeholder/statement/proved`。
6. `placeholder_policy_scope`：占位策略，`allowed/forbidden`。

## 文档生成与一致性
1. SSOT（Single Source of Truth）：单一事实源，这里是 `docs/ssot/registry.json`。
2. 派生文档：从 SSOT 自动生成的 Markdown（如 `INDEX.md`、`ModuleCatalog.md`）。
3. `sync_docs.py --write`：按固定模板生成文档。
4. `sync_docs.py --check`：重新生成一份“期望文本”，与当前文件逐字比较；任一不同就报错。
5. 固定模板：`tools/docs/sync_docs.py` 里的 `render_*` 函数（标题、列顺序、说明文字都写死）。

## Lean 构建与检查
1. `lake build`：构建整个 Lean 项目（解析 import、类型检查、生成产物）。
2. `import`：导入模块。
3. `#check`：检查某个名字是否存在、类型是否正确。
4. 冒烟检查（smoke）：用最小例子快速确认关键路径仍可编译。

## 质量门禁脚本
1. `check_no_sorry_axiom.sh`：扫描是否出现 `sorry` 或 `axiom`。
2. `sorry`：临时占位，表示证明未完成但先让编译通过。
3. `axiom`：直接引入未证明前提，会降低形式化可靠性。
4. `check_placeholder_policy.sh`：检查 `Core/Methods` 不允许 `Prop := True` 占位，并核对 SSOT 占位策略字段。
5. 占位允许范围：当前策略允许 `applications/books/legacy` 保留阶段性占位，不允许 `core/methods` 占位回归。

## 兼容层与导入回归
1. 兼容层：旧模块路径的薄封装文件，用于保持历史 `import` 不断。
2. 薄封装：文件本身不承载核心实现，主要转发到新分层模块。
3. 导入回归：`Eval/ImportSmoke.lean` 同时导入新路径和旧路径，验证重构后接口未断。

## 开发环境术语
1. symlink（符号链接）：类似快捷方式，指向另一个目录或文件。
2. submodule（Git 子模块）：在一个仓库中固定引用另一个仓库的某个提交。
3. MCP：Codex 使用的工具服务接入层；本项目用 `lean-lsp-mcp` 提供 Lean 交互能力。

## 常用命令（本仓）
1. `python3 tools/docs/validate_ssot.py`
2. `python3 tools/docs/sync_docs.py --check`
3. `python3 tools/docs/sync_docs.py --write`
4. `tools/ci/check_no_sorry_axiom.sh`
5. `tools/ci/check_placeholder_policy.sh`
6. `~/.elan/bin/lake env lean Eval/ImportSmoke.lean`
7. `~/.elan/bin/lake build`

## 常见报错（含义 -> 建议命令）
| 报错片段 | 含义（白话） | 先跑哪个命令 |
|---|---|---|
| `Derived docs are out of sync` | 生成后的文档和仓库里现有文档不一致 | `python3 tools/docs/sync_docs.py --write` 然后 `--check` |
| `missing keys` / `extra keys` | `registry.json` 字段不符合契约 | `python3 tools/docs/validate_ssot.py` 定位后修复 JSON 字段 |
| `bad import` | 导入路径无效或依赖没拉到本地 | 先 `~/.elan/bin/lake build`，再检查对应 `import` 路径是否存在 |
| `found forbidden token` | 出现了被禁止的 `sorry/axiom` | `tools/ci/check_no_sorry_axiom.sh` 定位并删除 |
| `Prop := True placeholders` | `Core/Methods` 出现不允许的占位 | `tools/ci/check_placeholder_policy.sh` 定位并改为真实 statement |
| `no such file or directory`（mathlib） | 依赖目录或路径不匹配 | `~/.elan/bin/lake build` 重新解析依赖并看首个失败点 |

## 术语反查（看到新词时怎么找定义）
1. 先在 `docs/Glossary.md` 看白话定义。
2. 再在 `docs/ssot/registry.json` 查该词对应的字段或模块路径。
3. 若是模块名（如 `MLTheory.X.Y`），用 `rg "MLTheory\.X\.Y" docs /Users/xiongjiangkai/xjk_papers/MLTheory/MLTheory` 找来源与引用。
4. 若是脚本术语（如 `placeholder_policy_scope`），用 `rg "placeholder_policy_scope" /Users/xiongjiangkai/xjk_papers/MLTheory/tools` 找校验逻辑。
5. 若是 CI 术语（如 `ImportSmoke`），看 `/Users/xiongjiangkai/xjk_papers/MLTheory/.github/workflows/lean_action_ci.yml` 对应步骤。
6. 仍不清楚时，优先问“这个词在哪个文件第几行生效”，避免语义歧义。
