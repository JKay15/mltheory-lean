# Lattimore & Szepesvari《Bandit Algorithms》 覆盖映射

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 书目信息
- 书名：Lattimore & Szepesvari《Bandit Algorithms》
- 版本：2020
- 覆盖日期：2026-02-13
- 维护人：Codex + 用户

## 目录来源与证据
1. `https://tor-lattimore.com/downloads/book/book.pdf`
2. `https://www.barnesandnoble.com/w/bandit-algorithms-tor-lattimore/1130390382`

## 章节覆盖表（SSOT 派生）
| 章节 | 对应模块 | 覆盖状态 | 证据链接 | 缺口说明 | 后续动作 |
|---|---|---|---|---|---|
| Ch1 | `MLTheory.Bandits.Foundations`, `MLTheory.Books.BanditAlgorithms.PartI_Foundations` | planned | 官方 PDF + 目录页 | 仅有规划，尚无定义与定理 | 先落多臂老虎机基础对象与 regret 定义。 |
| Ch2-Ch4 | `MLTheory.Bandits.Foundations`, `MLTheory.Probability.ProbIneq`, `MLTheory.Probability.Martingales` | partial | mathlib 概率/鞅基础 | 探索-利用算法证明链未落地 | 建 `ExploreThenCommit/UCB optimism` 占位定理。 |
| Ch5-Ch9 | `MLTheory.Bandits.Stochastic`, `MLTheory.Books.BanditAlgorithms.PartII_StochasticBandits` | partial | mathlib + 书目录 | UCB 下界、Bayesian regret、TS 证明缺口 | 先写问题与 regret 目标函数接口，再补上界/下界模板。 |
| Ch10-Ch14 | `MLTheory.Bandits.Adversarial`, `MLTheory.Books.BanditAlgorithms.PartIII_AdversarialBandits` | gap | 书目录 | EXP3/一二阶 regret 与 minimax 下界缺口大 | 先定义 adversarial protocol 和 benchmark，再补权重更新框架。 |
| Ch15-Ch23 | `MLTheory.Bandits.ContextualLinear`, `MLTheory.Bandits.InformationTheory`, `MLTheory.Books.BanditAlgorithms.PartIV_ContextualLinearBandits` | gap | 书目录 | 自归一化过程、线性 UCB/TS、核化 bandit 尚无现成实现 | 优先建立线性 bandit 记号层与置信椭球接口。 |
| Ch24 | `MLTheory.Bandits.LargeActionSpaces`, `MLTheory.Books.BanditAlgorithms.PartV_LargeActionSpaces` | gap | 书目录 | active arms 方向缺少基础 formalization | 先落动作筛选/活跃集定义。 |
| Ch25-Ch29 | `MLTheory.Bandits.BestArmIdentification`, `MLTheory.Bandits.Dueling`, `MLTheory.Bandits.PureExplorationLinear`, `MLTheory.Books.BanditAlgorithms.PartVI_PureExploration` | gap | 书目录 | BAI、dueling、线性纯探索均缺口 | 先写固定预算/固定置信定义与复杂度度量。 |
| Ch30-Ch38 | `MLTheory.Bandits.RLBridge`, `MLTheory.Books.BanditAlgorithms.PartVII_ReinforcementLearning` | gap | 书目录 | MDP regret、渐近 regret、burn-in 等尚未成体系 | 先建 bandit->MDP 桥接接口并标注与 RL 文献对齐点。 |
| Meta 书籍适配层索引 | `MLTheory.Bandits`, `MLTheory.Books`, `MLTheory.Books.BanditAlgorithms` | partial | SSOT 架构对齐 | 概念层与适配层锚点。 | 保持与 ModuleCatalog 同步。 |

## 与全局文档联动
1. 模块路径以 `../ModuleCatalog.md` 为唯一模块清单来源。
2. 缺口追踪以 `../GapLedger.md` 为唯一缺口台账来源。
3. 本文件仅保留章节覆盖映射，不重复维护全量模块表。
