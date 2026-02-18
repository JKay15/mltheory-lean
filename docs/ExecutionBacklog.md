# Planning execution checklist(Execution Backlog)

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## Understand at a glance
- Total number of planning modules:58
- Total number of execution shortlists:1
- Not scheduled(unscheduled):57
- explain:`near`=The last two rounds will be advanced,`mid`=Follow-up stage,`far`=long term exploration.

## near(Recently)
| priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|
| P3 | MLTheory.Core.Probability.CLTBridge | Probability | BasicMeasure Has landed,Continue to supplement the main line of probability and the connection layer of limit theorem,Service upstream concentration and learning interface. | form CLT bridge minimal interface(Standardization and,Extreme distribution occupancy interface)and access ImportSmoke. |

## mid(medium term)
| priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|

## far(forward)
| priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|

## Unscheduled modules(Top 25)
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

## Usage
1. Only from `near` Litori 1-2 Item advancement,Avoid quality degradation caused by excessive concurrency.
2. only completed `done_when`,Items are allowed to be moved from short-list Move out or downgrade to `mid/far`.
3. When adding a new planning module,Prioritize whether to enter `execution_backlog`,Otherwise default `unscheduled`.
