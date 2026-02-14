# Vershynin《High-Dimensional Probability》 覆盖映射

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 书目信息
- 书名：Vershynin《High-Dimensional Probability》
- 版本：2018
- 覆盖日期：2026-02-14
- 维护人：Codex + 用户

## 目录来源与证据
1. （暂无外部 URL；见对应章节的证据描述）

## 章节覆盖表（SSOT 派生）
| 章节 | 对应模块 | 覆盖状态 | 证据链接 | 缺口说明 | 后续动作 |
|---|---|---|---|---|---|
| Ch1 A Quick Refresher on Analysis and Probability | `MLTheory.Probability.Conditioning`, `MLTheory.Probability.LimitLaws`, `MLTheory.OR.ConvexCore`, `MLTheory.HDP.Ch01_Refresher` | partial | 见该书文档证据小节 | 凸分析/条件期望/极限定理基础可对接；按书级完整组织仍待补。 | 见 GapLedger 对应条目 |
| Ch2 Concentration of Sums of Independent Random Variables | `MLTheory.Probability.ProbIneq`, `MLTheory.Probability.Moments`, `MLTheory.HDP.Ch02_IndependentSums`, `MLTheory.Concentration` | partial | 见该书文档证据小节 | Hoeffding/Chernoff/SubGaussian 有基础；Subexponential/Bernstein/MoM 待补。 | 见 GapLedger 对应条目 |
| Ch3 Random Vectors in High Dimensions | `MLTheory.Probability.Moments`, `MLTheory.OR.StochasticMatrix`, `MLTheory.OR.GraphOptimization`, `MLTheory.HDP.Ch03_RandomVectors` | partial | 见该书文档证据小节 | 协方差、子高斯、矩阵基础可对接；PCA/Grothendieck/MaxCut 缺口较大。 | 见 GapLedger 对应条目 |
| Ch4 Random Matrices | `MLTheory.Learning.Capacity`, `MLTheory.OR.DiscreteOptimization`, `MLTheory.HDP.Ch04_RandomMatrices` | partial | 见该书文档证据小节 | covering/packing 与线代基础较强；应用侧（编码/社区检测）不足。 | 见 GapLedger 对应条目 |
| Ch5 Concentration Without Independence | `MLTheory.Probability.ProbIneq`, `MLTheory.Learning.Capacity`, `MLTheory.HDP.Ch05_WithoutIndependence` | gap | 见该书文档证据小节 | JL、Matrix Bernstein 等仍是缺口。 | 见 GapLedger 对应条目 |
| Ch6 Quadratic Forms, Symmetrization and Contraction | `MLTheory.Methods.Learning.Rademacher`, `MLTheory.Methods.Learning.Contraction`, `MLTheory.Learning.AdvancedSLT`, `MLTheory.HDP.Ch06_QuadraticSymmContraction` | gap | Vershynin TOC + MLTheory 通用工具模块 + `lean-stat-learning-theory` | Hanson-Wright/decoupling 仍需补齐；已建立 contraction 可复用接口 | 见 GapLedger 对应条目 |
| Ch7 Random Processes | `MLTheory.Learning.Sequential`, `MLTheory.Probability.Martingales`, `MLTheory.HDP.Ch07_RandomProcesses` | partial | 见该书文档证据小节 | process/martingale 基础可用；比较不等式链路未成体系。 | 见 GapLedger 对应条目 |
| Ch8 Chaining | `MLTheory.Learning.Capacity`, `MLTheory.Learning.AdvancedSLT`, `MLTheory.Learning.DiscreteModeling`, `MLTheory.Statistics`, `MLTheory.Statistics.Risk`, `MLTheory.Statistics.Information`, `MLTheory.LLM`, `MLTheory.LLM.Autoregressive`, `MLTheory.LLM.Sampling`, `MLTheory.LLM.AlignmentObjectives`, `MLTheory.HDP.Ch08_Chaining` | partial | 见该书文档证据小节 | Dudley/entropy integral 外部有高质量实现，但尚未并入本库。 | 见 GapLedger 对应条目 |
| Ch9 Deviations of Random Matrices on Sets | `MLTheory.Learning.AdvancedSLT`, `MLTheory.HDP.Ch09_MatrixDeviations` | gap | 见该书文档证据小节 | M*、escape、Dvoretzky-Milman 等尚缺。 | 见 GapLedger 对应条目 |
| Meta 概念分层对齐 | `MLTheory`, `MLTheory.Core`, `MLTheory.Methods`, `MLTheory.Applications`, `MLTheory.HDP`, `MLTheory.OR`, `MLTheory.Probability` | partial | SSOT 架构对齐 | 概念层与适配层锚点。 | 保持与 ModuleCatalog 同步。 |

## 与全局文档联动
1. 模块路径以 `../ModuleCatalog.md` 为唯一模块清单来源。
2. 缺口追踪以 `../GapLedger.md` 为唯一缺口台账来源。
3. 本文件仅保留章节覆盖映射，不重复维护全量模块表。
