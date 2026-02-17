# 术语白话表（Glossary）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 数据结构基础
1. JSON：一种数据格式，可表达对象（键值对）和数组（列表）。
2. root（最外层）：JSON 文件最外面那层对象。
3. 对象（object）：形如 `{ "键": 值 }`。
4. 数组（array）：形如 `[值1, 值2, ...]`。

## SSOT 根字段（`docs/ssot/registry.json`）
1. `meta`：项目全局信息（语言、toolchain、更新时间、策略、cleanup_release_epoch）。
2. `decisions`：决策日志（日期、决策、状态、影响）。
3. `taxonomy_nodes`：主树节点（主父关系 + tier 标签）。
4. `taxonomy_relations`：横向关系边（次父/关联 + 强度 0~1）。
5. `official_workflow_refs`：Lean 官方工作流能力与本仓落地点映射。
6. `canonical_specs`：canonical 入口契约（签名/禁词/依赖闭包）。
7. `modules`：真实模块清单（必须有本地 `.lean` 文件）。
8. `planned_modules`：规划模块清单（允许暂未落地文件）。
9. `execution_backlog`：规划短清单（`near/mid/far` + 优先级 + 完成定义）。
10. `structure_cleanup_candidates`：结构重整候选（执行状态、分批、兼容窗口、窗口数值、迁移起点、替代入口、风险、建议动作）。
11. `gaps`：缺口台账（没覆盖或部分覆盖的主题与后续动作）。
12. `books`：书籍覆盖映射（章节 -> 模块 -> 覆盖状态）。
13. `aliases`：兼容映射（旧模块路径 -> 新模块路径）。

## 模块相关术语
1. 模块（module）：一个可被 `import` 的 Lean 代码单元，通常对应一个 `.lean` 文件。
2. `module_path`：模块路径，如 `MLTheory.Core.Learning.PAC`。
3. `status`：覆盖状态，`planned/partial/covered/gap`。
3.1 对 `planned_modules`，`partial` 只允许用于“有可追溯外部证据”的条目；否则应使用 `planned` 或 `gap`。
4. `primary_node_id`：模块在 taxonomy 主树中的主归属节点。
5. `source_track`：来源轴（`native/books/legacy`）。
5.1 在 `modules` 中可取 `native/books/legacy`；在 `planned_modules` 中只允许 `native/books`。
5.2 `execution_backlog` 用于给 `planned_modules` 做短队列排期：`near`（近期）、`mid`（中期）、`far`（远期）。
6. `layer`：分层归属，`core/methods/applications/books/legacy`。
7. `proof_status`：证明进度，`placeholder/statement/proved`。
8. `placeholder_policy_scope`：占位策略，`allowed/forbidden`。
9. `role`：模块角色（canonical/compat/bridge/tool/placeholder）。
10. `user_surface`：对使用者是否作为公开入口（public/internal）。
11. `formal_decl_refs`：该模块承载的关键声明名清单。

## 文档生成与一致性
1. SSOT（Single Source of Truth）：单一事实源，这里是 `docs/ssot/registry.json`。
2. 派生文档：从 SSOT 自动生成的 Markdown（如 `INDEX.md`、`ModuleCatalog.md`）。
3. `sync_docs.py --write`：按固定模板生成文档。
4. `sync_docs.py --check`：重新生成一份“期望文本”，与当前文件逐字比较；任一不同就报错。
5. 固定模板：`tools/docs/sync_docs.py` 里的 `render_*` 函数（标题、列顺序、说明文字都写死）。
6. `NamespaceConvergence.md`：命名空间收敛视图（也是 SSOT 派生，不允许手改）。

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
6. `check_canonical_contract.sh`：检查 canonical 契约声明存在性、禁词与依赖引用。
7. `check_official_workflow_alignment.sh`：检查官方能力映射（Loogle/LeanSearch/InfoView/LoogleView/REPL）。
8. `check_tool_forest_consistency.py`：检查概念树与模块归属一致性。
9. `check_review_views_consistency.py`：检查 ReviewDashboard/APICards/交互页默认行为是否与 SSOT 一致。
10. `check_namespace_layout.py`：检查模块路径是否遵守分层前缀与 alias 收敛约束。
11. `check_no_new_deprecated_imports.sh`：禁止新增对已弃用兼容入口的 import（防回流）。
12. `check_ready_to_remove.py`：按 release 窗口自动判定是否应进入 `ready_to_remove`。
13. `check_registry_reference_hygiene.py`：检查 books/gaps 是否引用 deprecated alias，并检查 coverage 行是否出现重复模块。
14. `check_ssot_migration_idempotent.sh`：检查迁移脚本幂等性（当前 registry 运行迁移后不得产生 diff）。
15. `advance_cleanup_release_epoch.py`：推进 cleanup_release_epoch 并自动切换到期候选状态。
16. `StructureCleanupCandidates.md`：结构重整候选清单（本轮只清单，不删文件）。

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
6. `tools/ci/check_canonical_contract.sh`
7. `tools/ci/check_official_workflow_alignment.sh`
8. `python3 tools/ci/check_tool_forest_consistency.py`
9. `python3 tools/ci/check_review_views_consistency.py`
10. `python3 tools/ci/check_namespace_layout.py`
11. `tools/ci/check_no_new_deprecated_imports.sh`
12. `python3 tools/ci/check_ready_to_remove.py`
13. `python3 tools/ci/check_registry_reference_hygiene.py`
14. `tools/ci/check_ssot_migration_idempotent.sh`
15. `python3 tools/ci/advance_cleanup_release_epoch.py --to <N> --write`
16. `~/.elan/bin/lake env lean Eval/ImportSmoke.lean`
17. `~/.elan/bin/lake build`

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
