# Sutton-Barto《Reinforcement Learning: An Introduction》 覆盖映射

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 书目信息
- 书名：Sutton-Barto《Reinforcement Learning: An Introduction》
- 版本：Second Edition
- 覆盖日期：2026-02-18
- 维护人：Codex + 用户

## 目录来源与证据
1. `http://incompleteideas.net/book/the-book-2nd.html`
2. `https://mitpress.ublish.com/book/reinforcement-learning-an-introduction-2`

## 章节覆盖表（SSOT 派生）
| 章节 | 对应模块 | 覆盖状态 | 证据链接 | 缺口说明 | 后续动作 |
|---|---|---|---|---|---|
| Ch1 Introduction | `MLTheory.Books.SuttonBartoRL2`, `MLTheory.Methods.RL` | planned | 官方书页 + MIT TOC | 仅有规划入口 | 先统一 agent/environment/value/reward 术语层。 |
| Ch2 Multi-armed Bandits | `MLTheory.Books.SuttonBartoRL2.PartI_TabularMethods`, `MLTheory.Methods.Bandits.Foundations`, `MLTheory.Methods.Bandits.Stochastic` | partial | MIT TOC + Bandit 覆盖文档 | 书内算法链路未全部对齐 | 复用已有 bandit 模块并补 RL2 记号桥接。 |
| Ch3 Finite Markov Decision Processes | `MLTheory.Core.RL.MDP`, `MLTheory.Methods.RL.MDP`, `MLTheory.Methods.Bandits.RLBridge` | partial | MIT TOC + 本仓库占位模块 | 已有 MDP/Bellman 占位接口，完整定理链缺口仍在 | 在占位骨架上补 Bellman expectation/optimality theorem statement。 |
| Ch4 Dynamic Programming | `MLTheory.Methods.RL.DynamicProgramming` | partial | MIT TOC + 本仓库占位模块 | 已有 DP 更新与策略迭代占位，收敛证明缺口仍在 | 在占位骨架上补 policy iteration/value iteration 收敛陈述。 |
| Ch5 Monte Carlo Methods | `MLTheory.Methods.RL.MonteCarlo` | gap | MIT TOC | on/off-policy MC 主线未实现 | 增加重要性采样与 MC 控制接口。 |
| Ch6 Temporal-Difference Learning | `MLTheory.Methods.RL.TemporalDifference`, `MLTheory.Core.Probability.Martingales` | partial | MIT TOC + mathlib martingale 基础 | Sarsa/Q-learning/Expected Sarsa 缺口 | 在 TD 模块先补算法定义与误差递推接口。 |
| Ch7 n-step Bootstrapping | `MLTheory.Methods.RL.TemporalDifference` | gap | MIT TOC | n-step 统一框架缺口 | 增加 n-step return 与 tree-backup 占位。 |
| Ch8 Planning and Learning with Tabular Methods | `MLTheory.Methods.RL.ModelBasedPlanning`, `MLTheory.Methods.Bandits.RLBridge` | gap | MIT TOC | Dyna/MCTS/RTDP 缺口 | 先做 model-based planning 术语与接口。 |
| Ch9 On-policy Prediction with Approximation | `MLTheory.Books.SuttonBartoRL2.PartII_ApproximateMethods`, `MLTheory.Methods.RL.FunctionApproximation` | gap | MIT TOC | 逼近器与半梯度预测链路缺口 | 增加线性逼近与半梯度定义层。 |
| Ch10 On-policy Control with Approximation | `MLTheory.Methods.RL.FunctionApproximation` | gap | MIT TOC | 逼近控制主线缺口 | 增加半梯度控制占位接口。 |
| Ch11 Off-policy Methods with Approximation | `MLTheory.Methods.RL.OffPolicy` | gap | MIT TOC | deadly triad/GTD/ETD 体系缺口 | 建立 off-policy 稳定性占位层。 |
| Ch12 Eligibility Traces | `MLTheory.Methods.RL.EligibilityTraces` | gap | MIT TOC | TD(λ)/Sarsa(λ) 体系缺口 | 增加 λ-return 与 eligibility trace 接口。 |
| Ch13 Policy Gradient Methods | `MLTheory.Books.SuttonBartoRL2.PartII_ApproximateMethods`, `MLTheory.Methods.RL.PolicyGradient`, `MLTheory.Methods.OCO.OptimizationCore` | partial | MIT TOC + HazanOCO2 覆盖文档 | REINFORCE/actor-critic 未落地 | 在 policy gradient 模块补 log-derivative 接口。 |
| Ch14 Psychology | `MLTheory.Books.SuttonBartoRL2.PartIII_LookingDeeper`, `MLTheory.Methods.RL.PsychologyBridge` | gap | MIT TOC | 跨学科内容与当前模块耦合弱 | 先建术语桥接，不在 v0.1 深挖。 |
| Ch15 Neuroscience | `MLTheory.Methods.RL.NeuroscienceBridge` | gap | MIT TOC | 神经科学机制形式化缺口 | 先建 reward prediction error 术语层。 |
| Ch16 Applications and Case Studies | `MLTheory.Methods.RL.CaseStudies`, `MLTheory.Applications.AI.DecisionLearning` | gap | MIT TOC | 章节偏应用，缺抽象接口 | 先记录案例映射，不做重实现。 |
| Ch17 Frontiers | `MLTheory.Methods.RL.Frontiers`, `MLTheory.Applications.AI.DecisionLearning` | gap | MIT TOC | options/auxiliary tasks/reward design 缺口 | 建立 frontier 术语与开放问题台账。 |
| Meta 概念层 RL 接口 | `MLTheory.Core.RL`, `MLTheory.Core.RL.MDP`, `MLTheory.Methods.RL`, `MLTheory.Methods.RL.DynamicProgramming`, `MLTheory.Applications.RL` | partial | SSOT 架构对齐 | 概念层与适配层锚点。 | 保持与 ModuleCatalog 同步。 |

## 与全局文档联动
1. 模块路径以 `../ModuleCatalog.md` 为唯一模块清单来源。
2. 缺口追踪以 `../GapLedger.md` 为唯一缺口台账来源。
3. 本文件仅保留章节覆盖映射，不重复维护全量模块表。
