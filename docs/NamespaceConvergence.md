# 命名空间收敛视图（Namespace Convergence）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 目标（人话）
1. 新模块必须落在分层前缀下（`Core/Methods/Applications/Books`）。
2. `legacy` 层仅保留顶层兼容入口（`MLTheory.X`），不再新增深层 legacy 路径。
3. 旧入口统一通过 `aliases` 映射到新入口，避免“看起来还能 import，但不知道该改到哪里”。

## 当前收敛状态
- 当前 `structure_cleanup_candidates = 0`，兼容入口分批删除已完成。
- 真实模块总数：69
- alias 总数：22（deprecated=22 / active=0）

## 分层前缀约束（真实模块）
| layer | required_prefix | module_count | examples |
|---|---|---|---|
| core | MLTheory.Core | 14 | MLTheory.Core<br>MLTheory.Core.Learning<br>MLTheory.Core.Learning.Capacity |
| methods | MLTheory.Methods | 43 | MLTheory.Methods<br>MLTheory.Methods.Bandits<br>MLTheory.Methods.Bandits.Adversarial |
| applications | MLTheory.Applications | 9 | MLTheory.Applications.AI<br>MLTheory.Applications.AI.DecisionLearning<br>MLTheory.Applications.AI.Generalization |
| books | MLTheory.Books | 2 | MLTheory.Books.FoML2<br>MLTheory.Books.SuttonBartoRL2 |

## 剩余顶层 legacy 入口（保留兼容）
| module_path | source_track | role | status | proof_status |
|---|---|---|---|---|

## Deprecated Alias（旧入口 -> 新入口）
| legacy_module | canonical_module | status |
|---|---|---|
| MLTheory.AI | MLTheory.Applications.AI | deprecated |
| MLTheory.Applications | MLTheory.Applications.Learning | deprecated |
| MLTheory.Bandits | MLTheory.Methods.Bandits | deprecated |
| MLTheory.Books | MLTheory.Core | deprecated |
| MLTheory.Books.FoML2.Ch02_PACLearning | MLTheory.Core.Learning.PAC | deprecated |
| MLTheory.Books.FoML2.Ch03_RademacherVCDimension | MLTheory.Core.Learning.Capacity | deprecated |
| MLTheory.Books.FoML2.Ch04_ModelSelection | MLTheory.Methods.Learning.ModelSelection | deprecated |
| MLTheory.Books.FoML2.Ch05_SupportVectorMachines | MLTheory.Methods.Learning.SVM | deprecated |
| MLTheory.Books.FoML2.Ch06_KernelMethods | MLTheory.Methods.Learning.KernelMethods | deprecated |
| MLTheory.Books.SuttonBartoRL2.Ch03_MDP | MLTheory.Core.RL.MDP | deprecated |
| MLTheory.Books.SuttonBartoRL2.Ch04_DynamicProgramming | MLTheory.Methods.RL.DynamicProgramming | deprecated |
| MLTheory.Concentration | MLTheory.Methods.Learning.ConcentrationPackaging | deprecated |
| MLTheory.HDP | MLTheory.Core | deprecated |
| MLTheory.InfoTheory | MLTheory.Core.Statistics | deprecated |
| MLTheory.LLM | MLTheory.Applications.LLM | deprecated |
| MLTheory.Learning | MLTheory.Methods.Learning | deprecated |
| MLTheory.OCO | MLTheory.Methods.OCO | deprecated |
| MLTheory.OR | MLTheory.Methods.OR | deprecated |
| MLTheory.Optimization | MLTheory.Methods.OR | deprecated |
| MLTheory.Probability | MLTheory.Core.Probability | deprecated |
| MLTheory.RL | MLTheory.Core.RL | deprecated |
| MLTheory.Statistics | MLTheory.Core.Statistics | deprecated |

## Active Alias（仍处于兼容映射）
| legacy_module | canonical_module | status |
|---|---|---|
