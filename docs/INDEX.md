# MLTheory 文档索引

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 目的
本目录用于沉淀 MLTheory 的历史决策、模块规划、书籍覆盖情况与缺口检索台账。

## 核心导航
| 文档 | 说明 |
|---|---|
| [../AGENTS.md](../AGENTS.md) | 代理执行规范（文档系统优先、删除留痕规则） |
| [DecisionLog.md](./DecisionLog.md) | 决策日志（固定字段：`date/decision/status/impact`） |
| [ModuleCatalog.md](./ModuleCatalog.md) | 模块总表（固定字段：`module_path/primary_node_id/source_track/status/...`） |
| [GapLedger.md](./GapLedger.md) | 全局缺口台账（固定字段：`book/chapter/topic/status/last_search_date/sources_checked/candidate_repo/next_action`） |
| [ToolForest.md](./ToolForest.md) | 概念 + 模块森林图（由 SSOT 自动生成） |
| [ToolForestInteractive.html](./ToolForestInteractive.html) | 可筛选/可搜索/可折叠的交互式结构视图（推荐日常使用） |
| [GraphExplorer.html](./GraphExplorer.html) | 图谱视图 MVP（骨干优先 + 一跳展开，读取 subgraph） |
| [ReviewDashboard.md](./ReviewDashboard.md) | 验收看板（本轮新增、当前焦点、一键验收命令） |
| [RefactorHandoffForGPT52Pro.md](./RefactorHandoffForGPT52Pro.md) | 给 GPT5.2pro 的重构交接包（实现全景 + 门禁 + 风险） |
| [APICards.md](./APICards.md) | 最小 API 卡片（每个 public 模块做什么、先看哪些声明） |
| [ExecutionBacklog.md](./ExecutionBacklog.md) | 规划模块短清单（near/mid/far），把 96 条路线图收敛成可执行队列 |
| [NamespaceConvergence.md](./NamespaceConvergence.md) | 命名空间收敛视图（层级前缀、legacy 入口、alias 映射） |
| [StructureIssues.md](./StructureIssues.md) | 结构问题台账（自动识别问题 + 分批整改顺序 + 回滚点） |
| [StructureCleanupCandidates.md](./StructureCleanupCandidates.md) | 结构重整候选清单（分批/窗口/替代入口/风险） |
| [books/README.md](./books/README.md) | 书籍覆盖索引页 |
| [Glossary.md](./Glossary.md) | 术语白话表（减少黑话沟通成本） |
| [meta/taxonomy.yaml](./meta/taxonomy.yaml) | vNext 概念树与绑定（增量 meta） |
| [meta/aliases.yaml](./meta/aliases.yaml) | vNext 检索别名表（增量 meta） |
| [meta/canon.yaml](./meta/canon.yaml) | vNext 稳定 API 清单（增量 meta） |
| [_auto/README.md](./_auto/README.md) | 自动视图目录说明（生成入口） |
| [_auto/CodeIndex.md](./_auto/CodeIndex.md) | 代码优先模块/import 自动视图 |
| [_auto/GraphArtifacts.md](./_auto/GraphArtifacts.md) | 子图与 telemetry 统计自动视图 |
| [ssot/registry.json](./ssot/registry.json) | 单一事实源（唯一可手改数据文件） |
| [ssot/schema.json](./ssot/schema.json) | SSOT 字段契约 |

## 书籍覆盖文档
| 书籍 | 覆盖文档 |
|---|---|
| Vershynin《High-Dimensional Probability》 | [books/Vershynin_HDP_Coverage.md](./books/Vershynin_HDP_Coverage.md) |
| Durrett《Probability Theory and Examples》 | [books/Durrett5_Coverage.md](./books/Durrett5_Coverage.md) |
| Lattimore & Szepesvari《Bandit Algorithms》 | [books/BanditAlgorithms_Coverage.md](./books/BanditAlgorithms_Coverage.md) |
| Hazan《Introduction to Online Convex Optimization》 | [books/HazanOCO2_Coverage.md](./books/HazanOCO2_Coverage.md) |
| Mohri-Rostamizadeh-Talwalkar《Foundations of Machine Learning》 | [books/FoML2_Coverage.md](./books/FoML2_Coverage.md) |
| Sutton-Barto《Reinforcement Learning: An Introduction》 | [books/SuttonBarto_RL2_Coverage.md](./books/SuttonBarto_RL2_Coverage.md) |

## 维护规则（新增一本书时）
1. 先更新 `ssot/registry.json`，再运行文档生成脚本。
2. 执行 `python3 tools/docs/validate_ssot.py` 校验字段契约。
3. 执行 `python3 tools/docs/sync_docs.py --write` 生成派生文档。
4. 执行 `tools/index/gen_mltheory_index.sh` 更新 `artifacts/index` 与 `docs/_auto`。
5. 若有删除或替代，必须在 `DecisionLog.md` 留痕。

## ToolForest 快速上手
1. 验收当前一轮改动：先看 [ReviewDashboard.md](./ReviewDashboard.md)。
2. 要给重构模型完整上下文：看 [RefactorHandoffForGPT52Pro.md](./RefactorHandoffForGPT52Pro.md)。
3. 看模块用途与入口声明：再看 [APICards.md](./APICards.md)。
4. 看整体结构：打开 [ToolForestInteractive.html](./ToolForestInteractive.html)（默认只看真实模块）。
5. 看骨干+展开图谱：打开 [GraphExplorer.html](./GraphExplorer.html)。
6. 看索引统计与图谱统计：查看 [_auto/CodeIndex.md](./_auto/CodeIndex.md) + [_auto/GraphArtifacts.md](./_auto/GraphArtifacts.md)。
7. 要总览主树：看 [ToolForest.md](./ToolForest.md) 的“表 1：taxonomy 节点总览”。
8. 要看近期排期：看 [ExecutionBacklog.md](./ExecutionBacklog.md)。
9. 要看命名空间迁移路径：看 [NamespaceConvergence.md](./NamespaceConvergence.md)。
10. 要看结构问题与清理候选：看 [StructureIssues.md](./StructureIssues.md) + [StructureCleanupCandidates.md](./StructureCleanupCandidates.md)。
11. 任何结构调整都只能改 `ssot/registry.json`，再执行：
- `python3 tools/docs/validate_ssot.py`
- `python3 tools/docs/sync_docs.py --write`
- `tools/index/gen_mltheory_index.sh`
- `tools/index/gen_graph_artifacts.sh`
- `python3 tools/ci/check_taxonomy_contract.py`
- `python3 tools/ci/check_tool_forest_consistency.py`
- `python3 tools/ci/check_review_views_consistency.py`
- `python3 tools/ci/check_namespace_layout.py`
- `tools/ci/check_ssot_migration_idempotent.sh`
- `tools/ci/check_no_new_deprecated_imports.sh`
- `python3 tools/ci/check_ready_to_remove.py`
- `python3 tools/ci/check_registry_reference_hygiene.py`

## 当前默认约束
1. 文档语言：中文。
2. 文档组织：多文档索引制（不合并为单一总文档）。
3. 近期策略：先稳固 SSOT 与分层模块骨架，再逐章补证明。
4. 删除规则：不允许随意删除；有理由删除必须记录影响范围。
