# Mohri-Rostamizadeh-Talwalkar《Foundations of Machine Learning》 覆盖映射

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 书目信息
- 书名：Mohri-Rostamizadeh-Talwalkar《Foundations of Machine Learning》
- 版本：Second Edition
- 覆盖日期：2026-02-14
- 维护人：Codex + 用户

## 目录来源与证据
1. `https://mitpress.mit.edu/9780262039406/foundations-of-machine-learning/`
2. `https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/10290/Toc.pdf?dl=1`

## 章节覆盖表（SSOT 派生）
| 章节 | 对应模块 | 覆盖状态 | 证据链接 | 缺口说明 | 后续动作 |
|---|---|---|---|---|---|
| Ch1 Introduction | `MLTheory.Books.FoML2`, `MLTheory.Learning` | planned | MIT TOC PDF | 仅完成书级入口规划 | 保持章节映射为主，不复制模块清单。 |
| Ch2 PAC Learning Framework | `MLTheory.Books.FoML2.Ch02_PACLearning`, `MLTheory.Learning.Capacity`, `MLTheory.Probability.ProbIneq` | partial | MIT TOC PDF + 本仓库占位模块 | PAC 上下界证明链路不完整 | 在占位骨架上补 finite hypothesis set 定理陈述层。 |
| Ch3 Rademacher Complexity and VC-Dimension | `MLTheory.Books.FoML2.Ch03_RademacherVCDimension`, `MLTheory.Core.Learning.FunctionClass`, `MLTheory.Methods.Learning.Rademacher`, `MLTheory.Methods.Learning.Contraction`, `MLTheory.Methods.Learning.GeneralizationTools`, `MLTheory.Learning.AdvancedSLT` | partial | MIT TOC PDF + MLTheory 通用工具模块 + `lean-rademacher` + `lean-stat-learning-theory` | VC 维细节与书中完整常数链路仍待补齐 | 保持题目证明在 paper-template；MLTheory 继续补通用工具与记号桥接。 |
| Ch4 Model Selection | `MLTheory.Books.FoML2.Ch04_ModelSelection`, `MLTheory.Statistics.Risk`, `MLTheory.Learning.Capacity`, `MLTheory.OR.ConvexCore` | partial | MIT TOC PDF + 本仓库占位模块 | 已有目标函数占位，SRM/CV 保证链路缺口仍大 | 在占位骨架上补 SRM/CV 相关 theorem statement。 |
| Ch5 Support Vector Machines | `MLTheory.Books.FoML2.Ch05_SupportVectorMachines`, `MLTheory.OR.ConvexCore`, `MLTheory.Learning.Capacity` | partial | MIT TOC PDF + mathlib convex + 本仓库占位模块 | SVM 对偶与留一法分析未成体系 | 在占位骨架上补 primal/dual theorem statement。 |
| Ch6 Kernel Methods | `MLTheory.Books.FoML2.Ch06_KernelMethods`, `MLTheory.Learning.KernelBayes` | partial | MIT TOC PDF + mathlib kernel 基础 + 本仓库占位模块 | representer theorem 与序列核细节缺口 | 在占位骨架上补 representer theorem 接口。 |
| Ch7 Boosting | `MLTheory.OCO.Boosting`, `MLTheory.AI.DecisionLearning` | gap | MIT TOC PDF | AdaBoost 理论链与博弈解释未落地 | 与 Hazan OCO 的 boosting 模块共建接口。 |
| Ch8 On-Line Learning | `MLTheory.Learning.Sequential`, `MLTheory.OCO.OptimizationCore` | partial | MIT TOC PDF + HazanOCO2 覆盖文档 | 专家建议/感知机/Winnow 细节缺口 | 复用 OCO 定义后补 online-to-batch 桥接。 |
| Ch9 Multi-Class Classification | `MLTheory.Learning.DiscreteModeling`, `MLTheory.AI.DecisionLearning` | gap | MIT TOC PDF | 多分类组合策略与结构化预测缺口 | 先补 one-vs-all/one-vs-one 形式化接口。 |
| Ch10 Ranking | `MLTheory.Learning.DiscreteModeling`, `MLTheory.Statistics.Risk` | gap | MIT TOC PDF | ranking 损失与 AUC 证明缺口 | 在离散建模层补 ranking 指标定义。 |
| Ch11 Regression | `MLTheory.Learning.DiscreteModeling`, `MLTheory.Statistics.Risk`, `MLTheory.Probability.ProbIneq` | partial | MIT TOC PDF + mathlib | pseudo-dimension 与回归算法族缺口 | 补回归通用假设与泛化界模板。 |
| Ch12 Maximum Entropy Models | `MLTheory.Statistics.Information`, `MLTheory.OR.ConvexCore`, `MLTheory.InfoTheory` | gap | MIT TOC PDF | maxent 对偶与泛化界缺口 | 新增 maxent 模型与对偶问题占位。 |
| Ch13 Conditional Maximum Entropy Models | `MLTheory.Statistics.Information`, `MLTheory.OR.ConvexCore` | gap | MIT TOC PDF | 条件 maxent / logistic 统一视角缺口 | 在信息统计层补条件熵模型接口。 |
| Ch14 Algorithmic Stability | `MLTheory.AI.Generalization` | partial | MIT TOC PDF + mathlib 基础 | 稳定性到泛化界完整链路缺口 | 增加 stability-based generalization 定理占位。 |
| Ch15 Dimensionality Reduction | `MLTheory.OR.StochasticMatrix`, `MLTheory.Learning.Capacity` | partial | MIT TOC PDF + Vershynin 覆盖文档 | KPCA/流形学习/JL 的统一接口不足 | 复用 JL 缺口条目并补 KPCA 占位。 |
| Ch16 Learning Automata and Languages | `MLTheory.Learning.AutomataLanguage` | gap | MIT TOC PDF | 自动机学习主线在现有模块中缺失 | 新建 Automata/Language 占位模块并记录外部候选。 |
| Ch17 Reinforcement Learning | `MLTheory.Bandits.RLBridge`, `MLTheory.AI.DecisionLearning` | gap | MIT TOC PDF + Bandit 覆盖文档 | MDP/TD/Q-learning 体系缺口 | 与 Bandit Part VII 统一 RL 桥接层。 |
| Meta 概念层学习接口 | `MLTheory.Core.Learning`, `MLTheory.Core.Learning.PAC`, `MLTheory.Core.Learning.Capacity`, `MLTheory.Core.Learning.FunctionClass`, `MLTheory.Methods.Learning`, `MLTheory.Methods.Learning.Rademacher`, `MLTheory.Methods.Learning.Contraction`, `MLTheory.Methods.Learning.GeneralizationTools`, `MLTheory.Methods.Learning.ModelSelection`, `MLTheory.Methods.Learning.SVM`, `MLTheory.Methods.Learning.KernelMethods`, `MLTheory.Applications.Learning`, `MLTheory.AI`, `MLTheory.Methods.Learning.StoneWeierstrassBridge`, `MLTheory.Methods.Learning.ConcentrationPackaging` | partial | SSOT 架构对齐 | 概念层与适配层锚点。 | 保持与 ModuleCatalog 同步。 |

## 与全局文档联动
1. 模块路径以 `../ModuleCatalog.md` 为唯一模块清单来源。
2. 缺口追踪以 `../GapLedger.md` 为唯一缺口台账来源。
3. 本文件仅保留章节覆盖映射，不重复维护全量模块表。
