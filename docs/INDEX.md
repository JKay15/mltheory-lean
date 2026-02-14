# MLTheory 文档索引

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 目的
本目录用于沉淀 MLTheory 的历史决策、模块规划、书籍覆盖情况与缺口检索台账。

## 核心导航
| 文档 | 说明 |
|---|---|
| [../AGENTS.md](../AGENTS.md) | 代理执行规范（文档系统优先、删除留痕规则） |
| [DecisionLog.md](./DecisionLog.md) | 决策日志（固定字段：`date/decision/status/impact`） |
| [ModuleCatalog.md](./ModuleCatalog.md) | 模块总表（固定字段：`module_path/domain/status/source/book_refs`） |
| [GapLedger.md](./GapLedger.md) | 全局缺口台账（固定字段：`book/chapter/topic/status/last_search_date/sources_checked/candidate_repo/next_action`） |
| [books/README.md](./books/README.md) | 书籍覆盖索引页 |
| [Glossary.md](./Glossary.md) | 术语白话表（减少黑话沟通成本） |
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
4. 若有删除或替代，必须在 `DecisionLog.md` 留痕。

## 当前默认约束
1. 文档语言：中文。
2. 文档组织：多文档索引制（不合并为单一总文档）。
3. 近期策略：先稳固 SSOT 与分层模块骨架，再逐章补证明。
4. 删除规则：不允许随意删除；有理由删除必须记录影响范围。
