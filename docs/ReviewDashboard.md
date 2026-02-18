# Acceptance Kanban(Review Dashboard)

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## Look at these four things first
1. real module:`74`
2. planning module:`58`
3. Current short list:`1`
4. Recently promoted(planned -> file-backed):`10`

## Recently promoted(planned -> file-backed)
| module_path | node | role | proof_status | Read the statement first(Top3) |
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

## Current execution focus(execution_backlog)
| horizon | priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|---|
| near | P3 | MLTheory.Core.Probability.CLTBridge | Probability | BasicMeasure Has landed,Continue to supplement the main line of probability and the connection layer of limit theorem,Service upstream concentration and learning interface. | form CLT bridge minimal interface(Standardization and,Extreme distribution occupancy interface)and access ImportSmoke. |

## structural hot zone(Sort by planning pressure)
| node_name | node_id | real_modules | planned_modules |
|---|---|---|---|
| Probability | probability | 4 | 32 |
| RL | rl | 8 | 13 |
| Bandits | bandits | 11 | 8 |
| OCO | oco | 7 | 5 |
| Applications and Systems | applications_systems | 0 | 0 |
| Foundations | foundations | 0 | 0 |
| Methods and Problems | methods_problems | 0 | 0 |
| Support Infrastructure | support_infrastructure | 0 | 0 |

## One-click acceptance command
pass standard:All the above commands `PASS` / `Build completed successfully`.
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

## How to use(human language)
1. Check 'Recently promoted' first to confirm this batch matches the intended direction.
2. Then check 'Current execution focus' to confirm the next-step priority.
3. Finally run the 'One-click acceptance commands' to ensure independent reproducibility.
