# Vershynin《High-Dimensional Probability》 覆盖映射

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 书目信息
- 书名：Vershynin《High-Dimensional Probability》
- 版本：2018
- 覆盖日期：2026-02-18
- 维护人：Codex + 用户

## 目录来源与证据
1. （暂无外部 URL；见对应章节的证据描述）

## 章节覆盖表（SSOT 派生）
| 章节 | 对应模块 | 覆盖状态 | 证据链接 | 缺口说明 | 后续动作 |
|---|---|---|---|---|---|
| Ch1 A Quick Refresher on Analysis and Probability | `MLTheory.Core.Probability.Conditioning`, `MLTheory.Core.Probability.LimitLaws`, `MLTheory.Methods.OR.ConvexCore`, `MLTheory.Books.VershyninHDP.Ch01_Refresher` | partial | 见该书文档证据小节 | 凸分析/条件期望/极限定理基础可对接；按书级完整组织仍待补。 | 见 GapLedger 对应条目 |
| Ch2 Concentration of Sums of Independent Random Variables | `MLTheory.Core.Probability.ProbIneq`, `MLTheory.Core.Probability.Moments`, `MLTheory.Books.VershyninHDP.Ch02_IndependentSums`, `MLTheory.Methods.Learning.ConcentrationPackaging` | partial | 见该书文档证据小节 | Hoeffding/Chernoff/SubGaussian 有基础；Subexponential/Bernstein/MoM 待补。 | 见 GapLedger 对应条目 |
| Ch3 Random Vectors in High Dimensions | `MLTheory.Core.Probability.Moments`, `MLTheory.Methods.OR.StochasticMatrix`, `MLTheory.Methods.OR.GraphOptimization`, `MLTheory.Books.VershyninHDP.Ch03_RandomVectors` | partial | 见该书文档证据小节 | 协方差、子高斯、矩阵基础可对接；PCA/Grothendieck/MaxCut 缺口较大。 | 见 GapLedger 对应条目 |
| Ch4 Random Matrices | `MLTheory.Methods.Learning.Capacity`, `MLTheory.Methods.OR.DiscreteOptimization`, `MLTheory.Books.VershyninHDP.Ch04_RandomMatrices` | partial | 见该书文档证据小节 | covering/packing 与线代基础较强；应用侧（编码/社区检测）不足。 | 见 GapLedger 对应条目 |
| Ch5 Concentration Without Independence | `MLTheory.Core.Probability.ProbIneq`, `MLTheory.Methods.Learning.Capacity`, `MLTheory.Books.VershyninHDP.Ch05_WithoutIndependence` | gap | 见该书文档证据小节 | JL、Matrix Bernstein 等仍是缺口。 | 见 GapLedger 对应条目 |
| Ch6 Quadratic Forms, Symmetrization and Contraction | `MLTheory.Methods.Learning.Rademacher`, `MLTheory.Methods.Learning.Contraction`, `MLTheory.Methods.Learning.AdvancedSLT`, `MLTheory.Books.VershyninHDP.Ch06_QuadraticSymmContraction` | gap | Vershynin TOC + MLTheory 通用工具模块 + `lean-stat-learning-theory` | Hanson-Wright/decoupling 仍需补齐；已建立 contraction 可复用接口 | 见 GapLedger 对应条目 |
| Ch7 Random Processes | `MLTheory.Methods.Learning.Sequential`, `MLTheory.Core.Probability.Martingales`, `MLTheory.Books.VershyninHDP.Ch07_RandomProcesses` | partial | 见该书文档证据小节 | process/martingale 基础可用；比较不等式链路未成体系。 | 见 GapLedger 对应条目 |
| Ch8 Chaining | `MLTheory.Methods.Learning.Capacity`, `MLTheory.Methods.Learning.AdvancedSLT`, `MLTheory.Methods.Learning.DiscreteModeling`, `MLTheory.Core.Statistics`, `MLTheory.Core.Statistics.Risk`, `MLTheory.Core.Statistics.Information`, `MLTheory.Applications.LLM`, `MLTheory.Applications.LLM.Autoregressive`, `MLTheory.Applications.LLM.Sampling`, `MLTheory.Applications.LLM.AlignmentObjectives`, `MLTheory.Books.VershyninHDP.Ch08_Chaining` | partial | 见该书文档证据小节 | Dudley/entropy integral 外部有高质量实现，但尚未并入本库。 | 见 GapLedger 对应条目 |
| Ch9 Deviations of Random Matrices on Sets | `MLTheory.Methods.Learning.AdvancedSLT`, `MLTheory.Books.VershyninHDP.Ch09_MatrixDeviations` | gap | 见该书文档证据小节 | M*、escape、Dvoretzky-Milman 等尚缺。 | 见 GapLedger 对应条目 |
| Meta 概念分层对齐 | `MLTheory`, `MLTheory.Core`, `MLTheory.Methods`, `MLTheory.Applications.Learning`, `MLTheory.Books.VershyninHDP`, `MLTheory.Methods.OR`, `MLTheory.Core.Probability` | partial | SSOT 架构对齐 | 概念层与适配层锚点。 | 保持与 ModuleCatalog 同步。 |

## 与全局文档联动
1. 模块路径以 `../ModuleCatalog.md` 为唯一模块清单来源。
2. 缺口追踪以 `../GapLedger.md` 为唯一缺口台账来源。
3. 本文件仅保留章节覆盖映射，不重复维护全量模块表。
