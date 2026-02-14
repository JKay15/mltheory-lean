# Hazan《Introduction to Online Convex Optimization》 覆盖映射

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 书目信息
- 书名：Hazan《Introduction to Online Convex Optimization》
- 版本：Second Edition
- 覆盖日期：2026-02-13
- 维护人：Codex + 用户

## 目录来源与证据
1. `https://www.cs.princeton.edu/~ehazan/book2full.pdf`
2. `https://www.barnesandnoble.com/w/introduction-to-online-convex-optimization-elad-hazan/1147060507`

## 章节覆盖表（SSOT 派生）
| 章节 | 对应模块 | 覆盖状态 | 证据链接 | 缺口说明 | 后续动作 |
|---|---|---|---|---|---|
| Ch1 Introduction | `MLTheory.Books.HazanOCO2.PartI_Core`, `MLTheory.OCO` | planned | 目录来源 | 仅有规划入口 | 建立 OCO 术语与问题定义总入口。 |
| Ch2 Basic convex optimization | `MLTheory.OR.ConvexCore`, `MLTheory.OCO.OptimizationCore`, `MLTheory.Optimization` | partial | mathlib Convex.* | 书内算法化叙事未落地 | 将凸集/凸函数基础封装为 OCO 可用接口。 |
| Ch3 Online gradient descent | `MLTheory.OCO.OptimizationCore`, `MLTheory.Probability.ProbIneq` | partial | 目录 + mathlib 概率工具 | regret 证明链路缺口 | 增加 OGD regret theorem-statement 占位。 |
| Ch4 Second-order methods | `MLTheory.OCO.OptimizationCore` | gap | 目录来源 | ONS/self-concordance 缺口 | 增加二阶方法接口与假设层。 |
| Ch5 Regularization | `MLTheory.OCO.OptimizationCore` | partial | 目录来源 | FTRL/FTRL-Prox 证明缺失 | 增加 regularizer 与 update rule 抽象。 |
| Ch6 Bandit convex optimization | `MLTheory.Books.HazanOCO2.PartII_BanditAndGames`, `MLTheory.OCO.BanditConvex`, `MLTheory.Bandits.Stochastic` | gap | 目录来源 + Bandit 覆盖文档 | 连续动作 bandit 缺口 | 建立 bandit convex feedback 模型。 |
| Ch7 Projection-free OCO | `MLTheory.OCO.OptimizationCore` | gap | 目录来源 | online Frank-Wolfe 缺口 | 增加 projection-free 更新接口。 |
| Ch8 Games, duality, regret | `MLTheory.Books.HazanOCO2.PartII_BanditAndGames`, `MLTheory.OCO.GamesAndDuality`, `MLTheory.OCO.BanditConvex` | partial | 目录来源 | minimax/duality 形式化不完整 | 补零和博弈与 regret 对偶框架。 |
| Ch9 Learning theory, generalization and OCO | `MLTheory.Books.HazanOCO2.PartIII_GeneralizationAndAdaptivity`, `MLTheory.OCO.Generalization`, `MLTheory.AI.Generalization` | partial | 目录来源 + 现有 AI 模块 | 泛化边界与稳定性证明不足 | 先统一在线学习泛化接口。 |
| Ch10 Learning in changing environments | `MLTheory.Books.HazanOCO2.PartIII_GeneralizationAndAdaptivity`, `MLTheory.OCO.DynamicRegret`, `MLTheory.Learning.Sequential` | gap | 目录来源 | adaptive/dynamic regret 缺口 | 增加 comparator drift 与 dynamic regret 定义。 |
| Ch11 Boosting and regret minimization | `MLTheory.Books.HazanOCO2.PartIV_BoostingAndApproachability`, `MLTheory.OCO.Boosting`, `MLTheory.AI.DecisionLearning` | gap | 目录来源 | boosting-regret 联动缺口 | 增加 boosting->online learning 抽象桥接。 |
| Ch12 Online boosting | `MLTheory.Books.HazanOCO2.PartIV_BoostingAndApproachability`, `MLTheory.OCO.Boosting` | gap | 目录来源 | online boosting 算法与保证缺口 | 建立 weak learner/oracle 接口。 |
| Ch13 Blackwell approachability and OCO | `MLTheory.Books.HazanOCO2.PartIV_BoostingAndApproachability`, `MLTheory.OCO.GamesAndDuality` | gap | 目录来源 | approachability 方向缺口 | 增加 Blackwell set-valued payoff 抽象。 |
| Meta 书籍适配层索引 | `MLTheory.Books.HazanOCO2` | partial | SSOT 架构对齐 | 概念层与适配层锚点。 | 保持与 ModuleCatalog 同步。 |

## 与全局文档联动
1. 模块路径以 `../ModuleCatalog.md` 为唯一模块清单来源。
2. 缺口追踪以 `../GapLedger.md` 为唯一缺口台账来源。
3. 本文件仅保留章节覆盖映射，不重复维护全量模块表。
