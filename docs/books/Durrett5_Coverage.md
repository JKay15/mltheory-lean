# Durrett《Probability Theory and Examples》 覆盖映射

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 书目信息
- 书名：Durrett《Probability Theory and Examples》
- 版本：5th
- 覆盖日期：2026-02-14
- 维护人：Codex + 用户

## 目录来源与证据
1. （暂无外部 URL；见对应章节的证据描述）

## 章节覆盖表（SSOT 派生）
| 章节 | 对应模块 | 覆盖状态 | 证据链接 | 缺口说明 | 后续动作 |
|---|---|---|---|---|---|
| I Measure Theory | `MLTheory.Books.Durrett5.Ch01_MeasureTheory`, `MLTheory.Probability.BasicMeasure` | partial | 见该书文档证据小节 | 测度基础可复用，书级叙事需索引化补全。 | 见 GapLedger 对应条目 |
| II Probability Theory | `MLTheory.Books.Durrett5.Ch02_ProbabilityTheory`, `MLTheory.Probability.Conditioning`, `MLTheory.Probability.DensityCDF`, `MLTheory.Probability.ProbIneq` | partial | 见该书文档证据小节 | 条件期望、分布、尾界基础可接入。 | 见 GapLedger 对应条目 |
| III Independence, Expectations, and Sums | `MLTheory.Books.Durrett5.Ch03_IndependenceExpectations`, `MLTheory.Probability.Moments`, `MLTheory.Probability.LimitLaws` | partial | 见该书文档证据小节 | 独立性、矩、分布与 LLN 基础可用。 | 见 GapLedger 对应条目 |
| IV Limit Theorems | `MLTheory.Books.Durrett5.Ch04_LimitTheorems`, `MLTheory.Probability.CLTBridge`, `MLTheory.Probability.LimitLaws` | partial | 见该书文档证据小节 | SLLN 有，CLT 需桥接外部项目。 | 见 GapLedger 对应条目 |
| V Poisson Approximation | `MLTheory.Books.Durrett5.Ch05_PoissonApproximation`, `MLTheory.Probability.PoissonApprox` | gap | 见该书文档证据小节 | 目前缺少系统化 Poisson 近似/Stein 路线。 | 见 GapLedger 对应条目 |
| VI Markov Chains | `MLTheory.Books.Durrett5.Ch06_MarkovChains`, `MLTheory.Probability.MarkovKernels`, `MLTheory.Learning.KernelBayes` | partial | 见该书文档证据小节 | mathlib kernel 体系较强，Markov chain 书级接口待补。 | 见 GapLedger 对应条目 |
| VII Martingales | `MLTheory.Books.Durrett5.Ch07_Martingales`, `MLTheory.Probability.Martingales`, `MLTheory.Learning.Sequential` | partial | 见该书文档证据小节 | martingale 系列模块已有较高可用度。 | 见 GapLedger 对应条目 |
| VIII Brownian Motion | `MLTheory.Books.Durrett5.Ch08_BrownianMotion`, `MLTheory.Probability.Brownian` | gap | 见该书文档证据小节 | Brownian/Itô 需外部仓库或后续迁移。 | 见 GapLedger 对应条目 |
| IX Stationary Processes | `MLTheory.Books.Durrett5.Ch09_StationaryProcesses`, `MLTheory.Probability.Stationary` | gap | 见该书文档证据小节 | 平稳过程系统化模块不足。 | 见 GapLedger 对应条目 |
| X Continuous-Time Markov Chains | `MLTheory.Books.Durrett5.Ch10_CTMC`, `MLTheory.Probability.CTMC` | gap | 见该书文档证据小节 | CTMC 结构尚未成体系。 | 见 GapLedger 对应条目 |
| XI Ergodic Theorems | `MLTheory.Books.Durrett5.Ch11_ErgodicTheorems`, `MLTheory.Probability.Ergodic` | partial | 见该书文档证据小节 | dynamics/ergodic 可复用，但概率叙事层待补。 | 见 GapLedger 对应条目 |
| Meta 书籍适配层索引 | `MLTheory.Books.Durrett5` | partial | SSOT 架构对齐 | 概念层与适配层锚点。 | 保持与 ModuleCatalog 同步。 |

## 与全局文档联动
1. 模块路径以 `../ModuleCatalog.md` 为唯一模块清单来源。
2. 缺口追踪以 `../GapLedger.md` 为唯一缺口台账来源。
3. 本文件仅保留章节覆盖映射，不重复维护全量模块表。
