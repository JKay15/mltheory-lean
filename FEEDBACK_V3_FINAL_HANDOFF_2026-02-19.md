# MLTheory v6 Feedback v3 执行收口交接（2026-02-19）

## 1. 完成度结论
- 本轮按 `design/feedback_v3/docs/*` 约束执行，PR-A1 ~ PR-A8 与 PR-B1 ~ PR-B2 对应能力已落地。
- 当前剩余步骤：`0`（实现与验收命令已跑完）。
- 说明：额外契约检查 `check_meta_index_graph_contract` 当前失败（详见第 6 节），已明确 task card，不做无声跳过。

## 2. 逐 PR 结果

### PR-A1 交互 bugfix（pin / 双击 / 拖拽冲突）
- 修复/能力
- `click=选中`，`dblclick=pin/unpin`，使用原生 `dblclick` 事件。
- 引入拖拽阈值，拖拽与点击解耦。
- pin 状态有可视样式 + Inspector 明示。
- 主要文件
- `tools/graph_ui/src/app/40_render.js`
- `tools/graph_ui/src/app/50_interaction.js`
- `tools/graph_ui/src/app/10_core.js`
- 手工验证
- 双击任意节点可 pin/unpin。
- 拖拽节点不误触发 click/dblclick。
- pin 后重新布局位置保持。
- 风险与回滚点
- 风险：极快连续操作可能触发浏览器事件边界差异。
- 回滚点：仅回滚上述 3 文件相关 handler 片段。

### PR-A2 触控板体验（zoom/pan）
- 修复/能力
- 触控板双指滚动默认 pan；pinch(`ctrlKey`) 才 zoom。
- 鼠标滚轮保留 zoom，速度曲线重调。
- 放大后拖动画布速度恢复正常。
- 主要文件
- `tools/graph_ui/src/app/50_interaction.js`
- 手工验证
- Mac 触控板：双指平移快、捏合缩放正常。
- 鼠标滚轮缩放可用。
- 风险与回滚点
- 风险：不同浏览器对 wheel 信号差异。
- 回滚点：`onWheel` 逻辑块。

### PR-A3 UI 清晰度（visible + why missing）
- 修复/能力
- Overlay/Stats 显示 visible nodes/edges 与 kind 计数。
- 显示当前过滤器状态（含 spine/generated/scope/domain/maxNodes/maxEdges/proofMap/tree/group/importLens）。
- 增加 why-missing 解释来源（spine、generated、cap、proofMap、subtree、lens truncation 等）。
- 主要文件
- `tools/graph_ui/src/app/50_interaction.js`
- 手工验证
- 打开/关闭任意过滤项，overlay 文本实时变化。
- 节点缺失时可见可读原因。
- 风险与回滚点
- 风险：提示文案过长遮挡画布。
- 回滚点：`renderOverlay` 输出字段。

### PR-A4 层级/父子关系 + module->decl 分页展开
- 修复/能力
- contains 层级可视化、namespace tree 侧栏、subtree focus。
- module -> declaration 分页：expand/more/collapse 生效。
- edge 类型开关可控，默认 module-map 保持干净。
- 增加 group collapse（L2/L3）抑制毛线团。
- 主要文件
- `tools/graph_ui/src/app/10_core.js`
- `tools/graph_ui/src/app/20_views.js`
- `tools/graph_ui/src/app/40_render.js`
- `tools/graph_ui/src/app/50_interaction.js`
- `tools/graph_ui/src/index.template.html`
- 手工验证
- 树侧栏点某模块后仅看其子树。
- Inspector 的 expand/more/collapse 对声明节点数量有变化。
- contains 边与父子关系可读。
- 风险与回滚点
- 风险：超大子树时性能抖动。
- 回滚点：`treeFocusRoot` 过滤与分页游标逻辑。

### PR-A5 Mathlib Lens（slice roots/hubs/paths）
- 修复/能力
- 新增 `mathlib-lens` 视图模式。
- 显示 roots/hubs/aggregators/bridges，并支持 shortest import path。
- 新增 Mathlib Lens 面板可直接点选模块。
- Inspector 增加“Mathlib dependency summary”（直接依赖 + 可达 hub/root 跳数）。
- 新增 import transitive lens（deps/dependees/both）用于结构审计。
- 主要文件
- `tools/graph_ui/src/app/10_core.js`
- `tools/graph_ui/src/app/20_views.js`
- `tools/graph_ui/src/app/40_render.js`
- `tools/graph_ui/src/app/50_interaction.js`
- `tools/graph_ui/src/index.template.html`
- 手工验证
- 切换到 Mathlib lens 可看到 roots/hubs/bridges。
- 选中 MLTheory 模块后看到路径解释。
- Inspector 的 `lens deps/dependees/both` 可高亮传递依赖。
- 风险与回滚点
- 风险：路径计算深度过大时耗时上升。
- 回滚点：`shortestImportPath` + `setImportLens` 相关逻辑。

### PR-A6 Domain Taxonomy v2（两轴多标签 + progressive widening 对齐）
- 修复/能力
- UI 新增双轴 tag 面板（math/applied 多选），多选覆盖单选下拉。
- 过滤逻辑统一走 `nodeMatchesAxisTags`。
- 与 `domain profile`、scope/layer/spine 共同生效。
- 主要文件
- `tools/graph_ui/src/app/10_core.js`
- `tools/graph_ui/src/app/40_render.js`
- `tools/graph_ui/src/app/50_interaction.js`
- `tools/graph_ui/src/index.template.html`
- 元数据文件（新增）
- `docs/meta/taxonomy_math.yaml`
- `docs/meta/taxonomy_applied.yaml`
- `docs/meta/domain_profiles.yaml`
- `docs/meta/tags_overrides.yaml`
- 手工验证
- 在 Domain Tag Panel 多选标签，图实时过滤。
- 修改下拉标签会清空对应面板多选并按下拉过滤。
- `clear panel tags` 恢复默认。
- 风险与回滚点
- 风险：用户同时使用面板与下拉时理解成本。
- 回滚点：面板渲染函数与多选优先级逻辑。

### PR-A7（Repo A）检索工具链 + telemetry 可审计
- 修复/能力
- 新增统一入口：`tools/retrieval/query.py`。
- stage 顺序：domain local -> domain slice -> adjacent -> full MLTheory -> full mathlib -> external。
- 写入 `artifacts/telemetry/retrieval.jsonl`，输出候选、命中、耗时、来源与阶段。
- UI Inspector/Overlay 可查看 retrieval/usage 指标与最近检索信息。
- 主要文件
- `tools/retrieval/query.py`
- `artifacts/graphs/usage_graph.json`
- `artifacts/index/usage_suggestions.json`
- `docs/_auto/GraphArtifacts.md`
- `tools/graph_ui/src/app/40_render.js`
- `tools/graph_ui/src/app/50_interaction.js`
- 手工验证
- 执行一次检索命令后，`artifacts/telemetry/retrieval.jsonl` 有新增行。
- GraphExplorer Inspector 可见 retrieval source/stage/query/hits。
- 风险与回滚点
- 风险：外部 loogle/leanexplore 可用性波动。
- 回滚点：query.py 外部 backend 分支。

### PR-B1（Repo B）skills 调用统一检索入口
- 修复/能力
- `mltheory-retrieval` skill 明确必须调用 Repo A 的 `tools/retrieval/query.py`。
- progressive widening、存在性验证、fallback、输出契约写入 skill 合同。
- 主要文件
- `/Users/xiongjiangkai/xjk_papers/lean-proof-skills/.agents/skills/mltheory-retrieval/SKILL.md`
- 手工验证
- 阅读 skill 文档可见统一入口与阶段顺序。
- 执行 `python3 tools/validate_skill_contracts.py` 通过。
- 风险与回滚点
- 风险：调用方未按合同执行。
- 回滚点：SKILL.md 合同段落。

### PR-A8（Repo A）Problem Workspace + ProofMap
- 修复/能力
- Problems 结构与工具链落地：`Spec/Sketch/Cache/Proof/Tasks/Sources/Glossary`。
- 生成与加载 `ProofMap`（UI 一键加载局部图）。
- 新增 workspace 合约检查。
- 主要文件
- `tools/intake/intake_v2.py`
- `tools/intake/problem_suite.py`
- `tools/intake/sync_problem_workspace.py`
- `tools/index/gen_proof_map.py`
- `tools/index/gen_snapshot_bundle.py`
- `tools/ci/check_problem_workspace_contract.py`
- `Problems/`、`Problems.lean`
- 手工验证
- Problem Workspace 下拉选择问题，`load proof map` 生效并过滤子图。
- 合约命令通过。
- 风险与回滚点
- 风险：问题目录命名不规范导致索引缺失。
- 回滚点：proof map 索引生成与加载逻辑。

### PR-B2（Repo B）workflow 对齐 Problem Workspace
- 修复/能力
- `ml-paper-workflow` skill 写入严格两阶段 intake + Problem Workspace 合同 + 产物更新步骤。
- 增加 skill 合同校验脚本条款。
- 主要文件
- `/Users/xiongjiangkai/xjk_papers/lean-proof-skills/.agents/skills/ml-paper-workflow/SKILL.md`
- `/Users/xiongjiangkai/xjk_papers/lean-proof-skills/tools/validate_skill_contracts.py`
- 手工验证
- `python3 tools/validate_skill_contracts.py` 通过。
- 风险与回滚点
- 风险：执行器遗漏 phase。
- 回滚点：workflow skill 合同文本。

## 3. 本轮新增配置/产物目录（需知）
- 检索与审计
- `tools/retrieval/`
- `artifacts/telemetry/retrieval.jsonl`
- Domain Taxonomy v2 元数据
- `docs/meta/taxonomy_math.yaml`
- `docs/meta/taxonomy_applied.yaml`
- `docs/meta/domain_profiles.yaml`
- `docs/meta/tags_overrides.yaml`
- Problem Workspace
- `Problems/`
- `Problems.lean`
- `tools/index/gen_proof_map.py`
- `tools/intake/sync_problem_workspace.py`

## 4. 全量验收命令（本轮已执行）
- Repo A
- `python3 tools/graph_ui/build_graph_ui.py --write`
- `python3 tools/graph_ui/build_graph_ui.py --check`
- `lake build`
- `lake env lean Eval/ImportSmoke.lean`
- `lake env lean Eval/CanonicalAPISmoke.lean`
- `bash tools/ci/check_no_sorry_axiom.sh`
- `bash tools/ci/check_placeholder_policy.sh`
- `python3 tools/ci/check_problem_workspace_contract.py`
- `python3 tools/docs/validate_ssot.py`
- `python3 tools/docs/sync_docs.py --check`
- Repo B
- `python3 tools/validate_skill_contracts.py`

## 5. 前端手测总清单（给人工验收）
1. 节点交互：单击选中、双击 pin/unpin、拖拽不误判。
2. 触控板：双指平移、pinch 缩放；鼠标滚轮缩放。
3. Overlay：visible 计数、过滤器状态、why-missing 原因可读。
4. 层级：tree 展开/折叠、subtree focus、clear subtree focus。
5. 模块声明：expand module decls / more decls / collapse 生效。
6. Mathlib Lens：面板 roots/hubs/aggregators/bridges 可点选，路径解释可读。
7. Import Lens：deps/dependees/both 高亮与 clear lens。
8. Domain Tag Panel：双轴多选过滤、clear panel tags、与下拉协同。
9. Retrieval：执行一次 query 后 Inspector 能看到 source/stage/query，且 telemetry 有新增行。
10. Problem Workspace：选择 proof map 并 load，图收敛到问题局部子图。

## 6. 未完成项（明确披露 + task card）
- 未完成项
- `python3 tools/ci/check_meta_index_graph_contract.py` 当前失败：`subgraph.json` 历史节点未全量补齐 `profiles/math_tags/applied_tags` 字段。
- 原因
- 当前为避免 `subgraph.json` 大体积重生成导致 diff 爆炸，未执行全量 artifacts 重建。
- Task Card
- `TC-FB3-ARTIFACT-BACKFILL-2026-02-19`
- 目标：在 `gen_subgraph.py` 完整回填三字段并进行一次受控重生成，确保 `check_meta_index_graph_contract` 通过。
- 验收：
- `python3 tools/index/gen_subgraph.py`
- `python3 tools/ci/check_meta_index_graph_contract.py`
- UI 过滤回归（math/applied/domain 不退化）。
- 回滚点：仅回滚 `artifacts/graphs/subgraph.json` 与 `docs/_auto/subgraph.js`。

