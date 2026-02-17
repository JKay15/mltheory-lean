# 验收看板（Review Dashboard）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 你先看这四件事
1. 真实模块：`69`
2. 规划模块：`58`
3. 当前短清单：`1`
4. 最近提升（planned -> file-backed）：`10`

## 最近提升（planned -> file-backed）
| module_path | node | role | proof_status | 先看声明(Top3) |
|---|---|---|---|---|
| MLTheory.Core.Probability.BasicMeasure | Probability | tool | proved | isMeasurableEvent, eventMass, eventMass_mono, ...(+3) |
| MLTheory.Methods.Learning.DiscreteModeling | Learning | tool | proved | DiscreteModelingProblem, discretePointLoss, discreteEmpiricalRisk, ...(+3) |
| MLTheory.Methods.Learning.AutomataLanguage | Learning | tool | proved | AutomataLanguageProblem, runState, accepts, ...(+3) |
| MLTheory.Methods.Learning.KernelBayes | Learning | tool | proved | KernelBayesProblem, posteriorWeightUnnormalized, posteriorNormalization, ...(+3) |
| MLTheory.Methods.Learning.Sequential | Learning | tool | proved | SequentialLearningProblem, sequentialInstantLoss, sequentialPrefixRegret, ...(+3) |
| MLTheory.Methods.Learning.AdvancedSLT | Learning | tool | proved | AdvancedSLTProblem, advancedExcessRisk, complexityPenalty, ...(+3) |
| MLTheory.Methods.OCO.Boosting | OCO | tool | proved | BoostingRound, weightedExpertLoss, boostingInstantRegret, ...(+3) |
| MLTheory.Methods.OCO.GamesAndDuality | OCO | tool | proved | GameProblem, SaddleComparator, gameInstantRegret, ...(+3) |
| MLTheory.Methods.OCO.DynamicRegret | OCO | tool | proved | DynamicComparator, dynamicInstantRegret, dynamicCumulativeRegret, ...(+3) |
| MLTheory.Methods.OCO.BanditConvex | OCO | tool | proved | BanditConvexProblem, estimationGap, trueInstantRegret, ...(+3) |

## 当前执行焦点（execution_backlog）
| horizon | priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|---|
| near | P3 | MLTheory.Core.Probability.CLTBridge | Probability | BasicMeasure 已落地，继续补概率主线与极限定理连接层，服务上游 concentration 与 learning 接口。 | 形成 CLT bridge 最小接口（标准化和、极限分布占位接口）并接入 ImportSmoke。 |

## 结构热区（按规划压力排序）
| node_name | node_id | real_modules | planned_modules |
|---|---|---|---|
| Probability | probability | 4 | 32 |
| RL | rl | 8 | 13 |
| Bandits | bandits | 11 | 8 |
| OCO | oco | 7 | 5 |
| Applications and Systems | applications_systems | 0 | 0 |
| Foundations | foundations | 0 | 0 |
| MLTheory Root | ml_root | 0 | 0 |
| Methods and Problems | methods_problems | 0 | 0 |

## 一键验收命令
通过标准：以上命令全部 `PASS` / `Build completed successfully`。
```bash
python3 tools/docs/validate_ssot.py
python3 tools/docs/sync_docs.py --check
python3 tools/ci/check_taxonomy_contract.py
python3 tools/ci/check_tool_forest_consistency.py
python3 tools/ci/check_review_views_consistency.py
bash tools/ci/check_canonical_contract.sh
bash tools/ci/check_official_workflow_alignment.sh
bash tools/ci/check_no_sorry_axiom.sh
~/.elan/bin/lake build
```

## 怎么用（人话）
1. 先看“最近提升”，判断这批是否是你想要的方向。
2. 再看“当前执行焦点”，确认下一步是不是你认可的优先级。
3. 最后复制“ 一键验收命令 ”跑完，确保这轮变更可独立复验。
