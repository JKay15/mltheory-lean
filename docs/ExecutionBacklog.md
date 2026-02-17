# 规划执行清单（Execution Backlog）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 一眼看懂
- 规划模块总数：58
- 执行短清单总数：1
- 未排期（unscheduled）：57
- 解释：`near`=最近两轮就要推进，`mid`=后续阶段，`far`=远期探索。

## near（近期）
| priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|
| P3 | MLTheory.Core.Probability.CLTBridge | Probability | BasicMeasure 已落地，继续补概率主线与极限定理连接层，服务上游 concentration 与 learning 接口。 | 形成 CLT bridge 最小接口（标准化和、极限分布占位接口）并接入 ImportSmoke。 |

## mid（中期）
| priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|

## far（远期）
| priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|

## 未排期模块（Top 25）
| module_path |
|---|
| MLTheory.Books.BanditAlgorithms |
| MLTheory.Books.BanditAlgorithms.PartIII_AdversarialBandits |
| MLTheory.Books.BanditAlgorithms.PartII_StochasticBandits |
| MLTheory.Books.BanditAlgorithms.PartIV_ContextualLinearBandits |
| MLTheory.Books.BanditAlgorithms.PartI_Foundations |
| MLTheory.Books.BanditAlgorithms.PartVII_ReinforcementLearning |
| MLTheory.Books.BanditAlgorithms.PartVI_PureExploration |
| MLTheory.Books.BanditAlgorithms.PartV_LargeActionSpaces |
| MLTheory.Books.Durrett5 |
| MLTheory.Books.Durrett5.Ch01_MeasureTheory |
| MLTheory.Books.Durrett5.Ch02_ProbabilityTheory |
| MLTheory.Books.Durrett5.Ch03_IndependenceExpectations |
| MLTheory.Books.Durrett5.Ch04_LimitTheorems |
| MLTheory.Books.Durrett5.Ch05_PoissonApproximation |
| MLTheory.Books.Durrett5.Ch06_MarkovChains |
| MLTheory.Books.Durrett5.Ch07_Martingales |
| MLTheory.Books.Durrett5.Ch08_BrownianMotion |
| MLTheory.Books.Durrett5.Ch09_StationaryProcesses |
| MLTheory.Books.Durrett5.Ch10_CTMC |
| MLTheory.Books.Durrett5.Ch11_ErgodicTheorems |
| MLTheory.Books.HazanOCO2 |
| MLTheory.Books.HazanOCO2.PartIII_GeneralizationAndAdaptivity |
| MLTheory.Books.HazanOCO2.PartII_BanditAndGames |
| MLTheory.Books.HazanOCO2.PartIV_BoostingAndApproachability |
| MLTheory.Books.HazanOCO2.PartI_Core |

## 使用方式
1. 每次只从 `near` 里取 1-2 项推进，避免并发过多导致质量下降。
2. 只有完成 `done_when`，才允许把条目从 short-list 移出或降级到 `mid/far`。
3. 新增规划模块时，优先决定是否进入 `execution_backlog`，否则默认 `unscheduled`。
