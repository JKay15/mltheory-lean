# AGENTS.md

本文件定义本仓库的代理执行规范。后续所有任务默认都要遵循这里的规则。

## 1. 文档系统优先（SSOT）
1. 开始任何新任务前，先看 `docs/INDEX.md`。
2. 文档数据的单一事实源固定为：`docs/ssot/registry.json`。
3. `docs/*.md` 与 `docs/books/*.md`（含索引、覆盖、台账）均为派生文件，禁止直接手改正文数据。
4. 文档改动流程固定为：
- 先改 `docs/ssot/registry.json`
- 执行 `python3 tools/docs/validate_ssot.py`
- 执行 `python3 tools/docs/sync_docs.py --write`
5. 产生了新信息（新决策、新模块、新缺口、新外部候选）必须回写到 `registry.json`，并重新生成文档。

## 1.1 三仓协同约束（固定）
1. 论文模板仓（最外层）是运行入口。
2. `lean-proof-skills` 是 skillpack 父仓，内部包含 `lean4` 与 `ml-paper-workflow`。
3. `MLTheory` 由模板仓通过 Lake `git + rev(tag)` 依赖，不使用 submodule。
4. skills 使用优先级：repo-scope（模板仓 `.agents/skills/*`）优先于全局 `~/.codex/skills/*`。

## 2. 结构与命名
1. 文档语言默认中文。
2. 日期统一使用 `YYYY-MM-DD`。
3. 模块名必须与 `docs/ModuleCatalog.md`（由 SSOT 生成）的 `module_path` 完全一致。
4. 新增书籍时必须基于 `docs/books/_BookCoverageTemplate.md`。
5. 代码组织遵循概念优先分层：
- `MLTheory/Core/*`
- `MLTheory/Methods/*`
- `MLTheory/Applications/*`
- `MLTheory/Books/*`（兼容适配与重导出）

## 3. 删除策略（重要）
1. 默认策略：不随意删除（append-first）。
2. 允许删除，但必须满足以下条件：
- 删除有明确理由（错误、重复、过时且已替代）。
- 在 `registry.json` 增加对应决策记录，并重新生成 `docs/DecisionLog.md`。
- 优先“标记废弃/迁移归档”，再考虑物理删除。
3. 未记录理由的删除视为违规。

## 4. 执行最小要求
1. 每次提交前至少执行：
- `python3 tools/docs/validate_ssot.py`
- `python3 tools/docs/sync_docs.py --check`
- `lake build`
2. 每次提交前至少执行一次文档检索自检（例如 `rg`）确保关键字段存在。
3. 保持 `docs/INDEX.md` 可作为唯一导航入口，新增核心文档必须补链接。

## 4.1 占位门禁策略（固定）
1. Phase 1：允许 `Applications/Books/Legacy` 层占位。
2. Phase 1 同时要求：`Core/Methods` 层占位必须为 0。
3. Phase 2：CI 对 `Core/Methods` 占位回归直接失败（硬门禁）。

## 5. 冲突处理
1. 如果本文件与用户最新明确指令冲突，以用户指令为准。
2. 若存在歧义，先按“保留信息、最小删除、先记录后变更”的方向处理。
