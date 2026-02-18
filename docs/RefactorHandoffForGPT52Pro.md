# GPT5.2pro Refactoring the handover package(MLTheory Full implementation snapshot)

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## Purpose(Give reconstruction model)
1. This document is a snapshot of completed work to avoid context loss during refactoring.
2. All data comes from `docs/ssot/registry.json`(and review documents `docs/ssot/lean4_contract_audit.json`).
3. You can feed this document directly to GPT5.2pro,Let it update the reconstruction plan based on the real status quo.

## Understand the current status at a glance
- SSOT schema_version:`1.4.0`
- last_updated:`2026-02-18`
- Total number of decisions:`167`
- real module(file-backed)total:`69`
- planning module(non-file-backed)total:`58`
- Execute short list(execution_backlog)number of items:`1`
- aliases total:`22`
- gaps total:`55`

## Current next step(short list)
| horizon | priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|---|
| near | P3 | MLTheory.Core.Probability.CLTBridge | Probability | BasicMeasure Has landed,Continue to supplement the main line of probability and the connection layer of limit theorem,Service upstream concentration and learning interface. | form CLT bridge minimal interface(Standardization and,Extreme distribution occupancy interface)and access ImportSmoke. |

## architectural contract(Unbreakable by default when refactoring)
### 1) taxonomy main tree
| node_id | name | tier | primary_parent_id | status | order |
|---|---|---|---|---|---|
| ml_root | MLTheory Root | support | root | active | 0 |
| foundations | Foundations | foundation | ml_root | active | 10 |
| methods_problems | Methods and Problems | methods | ml_root | active | 20 |
| applications_systems | Applications and Systems | application | ml_root | active | 30 |
| support_infrastructure | Support Infrastructure | support | ml_root | active | 40 |
| probability | Probability | foundation | foundations | active | 100 |
| statistics | Statistics | foundation | foundations | active | 110 |
| learning | Learning | methods | methods_problems | active | 200 |
| or | OR | methods | methods_problems | active | 210 |
| rl | RL | methods | learning | active | 220 |
| oco | OCO | methods | or | active | 230 |
| bandits | Bandits | methods | or | active | 240 |
| ai | AI | application | learning | active | 300 |
| llm | LLM | application | ai | active | 310 |
| architecture | Architecture | support | support_infrastructure | active | 400 |

### 2) taxonomy relationship edge(secondary_parent/related)
| from_node | from_name | to_node | to_name | relation_type | strength |
|---|---|---|---|---|---|
| statistics | Statistics | probability | Probability | related | 0.8 |
| rl | RL | ai | AI | related | 0.6 |
| bandits | Bandits | rl | RL | related | 0.8 |

### 3) Official workflow alignment(Lean Official resource mapping)
| capability | source_url | status | local_enforcement |
|---|---|---|---|
| Loogle | https://lean-lang.org/learn/ | active | lean-lsp-mcp: `lean_loogle` + `--loogle-local`;CI: tools/ci/check_official_workflow_alignment.sh |
| LeanSearch | https://lean-lang.org/learn/ | active | lean-lsp-mcp: `lean_leansearch`;CI: tools/ci/check_official_workflow_alignment.sh |
| InfoView/LoogleView | https://raw.githubusercontent.com/leanprover/vscode-lean4/master/vscode-lean4/manual/manual.md | active | lean-lsp-mcp: `lean_goal` + `lean_diagnostic_messages`;augmented The pattern requires key conclusions to be made InfoView/LoogleView Manual review and record into contract review instructions(formalization-contract skill) |
| REPL | https://lean-lang.org/learn/ | active | lean-lsp-mcp The startup parameters are required to include `--repl`;CI: tools/ci/check_official_workflow_alignment.sh |

### 4) canonical spec contract
| spec_id | repo | entry_file | entry_decl | axiom_policy | status | required_decl_refs |
|---|---|---|---|---|---|---|
| mltheory_pac_badEvent_uniform_bound | MLTheory | MLTheory/Methods/Learning/GeneralizationTools.lean | pac_badEvent_uniform_bound | standard_only | active | pac_badEvent_uniform_bound, pac_badEvent_union_bound |
| mltheory_stone_exists_uniform_near | MLTheory | MLTheory/Methods/Learning/StoneWeierstrassBridge.lean | stone_exists_uniform_near | standard_only | active | stone_exists_uniform_near, stone_closure_eq_top |

## Phase-0 / skill Alignment review snapshot
- date=2026-02-17;mode=augmented;score=6/10;status=ok
| # | check_id | title | result | hits |
|---|---|---|---|---|
| 1 | build_gate | Build access control(lake build) | PASS | 1 |
| 2 | sorry_zero_gate | sorry Clear access control | PASS | 1 |
| 3 | axiom_whitelist_gate | Customize axiom Whitelist access control | PASS | 4 |
| 4 | declaration_immutability | Theorem states that rules cannot be changed privately | PASS | 1 |
| 5 | checkpoint_reproducible | Reproducible checkpoint process | PASS | 2 |
| 6 | canonical_signature_lock | canonical Entry signature lock | FAIL | 2 |
| 7 | dependency_closure_verifiable | Dependency closure is verifiable(Declarative level) | PASS | 2 |
| 8 | intermediate_to_canonical_mapping | intermediate concept to canonical Mapping constraints | FAIL | 0 |
| 9 | official_toolchain_mapping | Official toolchain mapping constraints(Loogle/LeanSearch/InfoView/REPL) | FAIL | 2 |
| 10 | three_repo_boundary | Three warehouse boundary constraints | FAIL | 0 |

## Completed implementation(planned -> file-backed Ascension trajectory)
| date | module_path | node | state(layer/role/proof) | impact |
|---|---|---|---|---|
| 2026-02-16 | MLTheory.Core.Probability.ProbIneq | Probability | core/tool/proved | The probability core layer is newly added and reusable conditioning/inequality Entrance,execution_backlog of near The item begins to be substantially digested. |
| 2026-02-16 | MLTheory.Core.Statistics.Risk | Statistics | core/tool/proved | New statistics core layer risk semantic shell,near The short list further converges. |
| 2026-02-16 | MLTheory.Methods.OR.ConvexCore | OR | methods/tool/proved | OR Added convex optimization core abstraction to the method layer,near backlog Continue to converge. |
| 2026-02-16 | MLTheory.Methods.Bandits.Foundations | Bandits | methods/canonical/proved | Bandits The method layer forms a unified foundations Entrance,near backlog continue to shorten. |
| 2026-02-16 | MLTheory.Methods.OCO.OptimizationCore | OCO | methods/tool/proved | OCO Main line completion problem definition/comparator/update abstract,execution_backlog Recent projects are completed and entered into the next mid-term queue. |
| 2026-02-16 | MLTheory.Methods.Bandits.Stochastic | Bandits | methods/tool/proved | Bandits Main line completion UCB/ETC Minimally declare a shell and reuse it Foundations regret interface,The recent queue continues to OCO/RL Mid-term project promotion. |
| 2026-02-16 | MLTheory.Methods.OCO.Generalization | OCO | methods/tool/proved | OCO->Learning of online-to-batch Minimum bridge interface implemented,execution_backlog The recent focus is postponed to RL.MDP. |
| 2026-02-16 | MLTheory.Methods.RL.MDP | RL | methods/tool/proved | RL Method layer completion MDP Inlet shell and align Core/DP interface,execution_backlog The recent focus is postponed to TemporalDifference. |
| 2026-02-16 | MLTheory.Methods.RL.TemporalDifference | RL | methods/tool/proved | RL Main line completion TD Update and error recursion interface;execution_backlog The recent focus is postponed to Applications.AI.Generalization. |
| 2026-02-16 | MLTheory.Applications.AI.Generalization | AI | applications/tool/proved | Application layer AI The generalized bridge entrance is implemented without adding new underlying concepts.;execution_backlog The recent focus is postponed to Applications.LLM.Autoregressive. |
| 2026-02-16 | MLTheory.Applications.LLM.Autoregressive | LLM | applications/tool/proved | Application layer LLM The self-returning entrance is implemented and reused AI generalized contract;current execution_backlog Clear,The next batch needs to be manually determined later. near queue. |
| 2026-02-16 | MLTheory.Core.Statistics.Information | Statistics | core/tool/proved | New main line of statistical information theory KL/maxent/conditional-gap minimal interface,The recent focus is postponed to Methods.Learning.Capacity. |
| 2026-02-16 | MLTheory.Methods.Learning.Capacity | Learning | methods/tool/proved | Learning Method layer completion capacity/JL Place the interface and connect to the probabilistic tail-bound bridge;The recent focus is postponed to Applications.AI.DecisionLearning. |
| 2026-02-16 | MLTheory.Applications.AI.DecisionLearning | AI | applications/tool/proved | AI Application layer completion decision-learning Scene entry and reuse Learning/OCO/RL interface;The recent focus is postponed to Applications.LLM.Sampling. |
| 2026-02-16 | MLTheory.Applications.LLM.Sampling | LLM | applications/tool/proved | LLM Application layer completion sampling Policy minimal interface and with autoregressive contract alignment;The recent focus is postponed to Applications.LLM.AlignmentObjectives. |
| 2026-02-16 | MLTheory.Applications.LLM.AlignmentObjectives | LLM | applications/tool/proved | LLM Application layer completion alignment objective entrance and with sampling/autoregressive Contract opening;Recent focus switches to Methods.Bandits.InformationTheory. |
| 2026-02-16 | MLTheory.Methods.Bandits.InformationTheory | Bandits | methods/tool/proved | Bandits Method layer completion information-theoretic bonus/regret Entry and reuse cumulativeRegret;Recent focus switches to Methods.Bandits.Adversarial. |
| 2026-02-16 | MLTheory.Methods.Bandits.Adversarial | Bandits | methods/tool/proved | Bandits Method layer completion adversarial regret/EXP3 Entry and share with cumulativeRegret Alignment;Recent focus switches to Methods.Bandits.BestArmIdentification. |
| 2026-02-16 | MLTheory.Methods.Bandits.BestArmIdentification | Bandits | methods/tool/proved | Bandits Method layer completion BAI/simple-regret/sample-complexity minimal interface;Recent focus switches to Methods.Bandits.ContextualLinear. |
| 2026-02-16 | MLTheory.Methods.Bandits.ContextualLinear | Bandits | methods/tool/proved | Bandits Method layer completion contextual-linear problem definition/confidence radius/regret Entrance;Recent focus switches to Methods.Bandits.Dueling. |
| 2026-02-17 | MLTheory.Methods.Bandits.Dueling | Bandits | methods/tool/proved | Bandits Method layer completion dueling Preference feedback and regret Entrance;Recent focus switches to Methods.Bandits.LargeActionSpaces. |
| 2026-02-17 | MLTheory.Methods.Bandits.LargeActionSpaces | Bandits | methods/tool/proved | Bandits The method layer completes the large action space candidate pool size and regret Entrance;Recent focus switches to Methods.Bandits.PureExplorationLinear. |
| 2026-02-17 | MLTheory.Methods.Bandits.PureExplorationLinear | Bandits | methods/tool/proved | Bandits Method layer completion pure-exploration-linear The error radius of simple-regret interface;Recent focus switches to Methods.Bandits.RLBridge. |
| 2026-02-17 | MLTheory.Methods.Bandits.RLBridge | Bandits | methods/tool/proved | Bandits Method layer completion and RL.TD bridge interface;Recent focus switches to Methods.OR.DiscreteOptimization. |
| 2026-02-17 | MLTheory.Methods.OR.DiscreteOptimization | OR | methods/tool/proved | Methods.OR Form a discrete optimized minimal interface and reuse it ConvexCore.objectiveGap;Recent focus switches to Methods.OR.GraphOptimization. |
| 2026-02-17 | MLTheory.Methods.OR.GraphOptimization | OR | methods/tool/proved | Methods.OR Completion graph optimization minimal interface(path/Cut the gap)and reuse ConvexCore.objectiveGap;Recent focus switches to Methods.OR.StochasticMatrix. |
| 2026-02-17 | MLTheory.Methods.OR.StochasticMatrix | OR | methods/tool/proved | Methods.OR The minimum interface of random matrix is ​​implemented and reused ConvexCore.objectiveGap;OR Three recent completions,Recent focus switches to Methods.OCO.BanditConvex. |
| 2026-02-17 | MLTheory.Methods.OCO.BanditConvex | OCO | methods/tool/proved | Methods.OCO Increase bandit-convex estimate/Sorry gap interface and reuse OCO regret core;Recent focus switches to Methods.OCO.DynamicRegret. |
| 2026-02-17 | MLTheory.Methods.OCO.DynamicRegret | OCO | methods/tool/proved | Methods.OCO Added dynamic comparator and dynamic regret minimum interface;Recent focus switches to Methods.OCO.GamesAndDuality. |
| 2026-02-17 | MLTheory.Methods.OCO.GamesAndDuality | OCO | methods/tool/proved | Methods.OCO complete games/duality minimal interface(Game Regret and Duality Gap);Recent focus switches to Methods.OCO.Boosting. |
| 2026-02-17 | MLTheory.Methods.OCO.Boosting | OCO | methods/tool/proved | Methods.OCO All closings awaiting completion in the near future;Recent focus switches to Methods.Learning.AdvancedSLT. |
| 2026-02-17 | MLTheory.Methods.Learning.AdvancedSLT | Learning | methods/tool/proved | Methods.Learning complete advanced SLT minimal interface;Recent focus switches to Methods.Learning.Sequential. |
| 2026-02-17 | MLTheory.Methods.Learning.Sequential | Learning | methods/tool/proved | Methods.Learning complete sequential Learn the minimal interface and connect OCO regret definition;Recent focus switches to Methods.Learning.KernelBayes. |
| 2026-02-17 | MLTheory.Methods.Learning.KernelBayes | Learning | methods/tool/proved | Learning Main line completion kernel-Bayes Posterior update and risk gap minimum interface,execution_backlog The recent focus is postponed to AutomataLanguage. |
| 2026-02-17 | MLTheory.Methods.Learning.AutomataLanguage | Learning | methods/tool/proved | Learning A new discrete automaton language risk interface is added to the sub-line.,execution_backlog The recent focus is postponed to DiscreteModeling. |
| 2026-02-17 | MLTheory.Methods.Learning.DiscreteModeling | Learning | methods/tool/proved | Learning Three items on the short list for the near future(KernelBayes/AutomataLanguage/DiscreteModeling)All have been implemented,execution_backlog Complete the basic transfer probability. |
| 2026-02-17 | MLTheory.Core.Probability.BasicMeasure | Probability | core/tool/proved | foundations Probability layer completes the measurement basic entrance,execution_backlog The recent focus is postponed to CLTBridge. |

## Full list of real modules(Implementation details)
| module_path | file_path | node | source_track | layer | role | proof_status | formal_decl_refs |
|---|---|---|---|---|---|---|---|
| MLTheory | MLTheory.lean | Architecture | native | legacy | bridge | statement |  |
| MLTheory.Applications.AI | MLTheory/Applications/AI.lean | AI | native | applications | bridge | statement |  |
| MLTheory.Applications.AI.DecisionLearning | MLTheory/Applications/AI/DecisionLearning.lean | AI | native | applications | tool | proved | DecisionLearningScenario, policyImprovementGap, policyImprovementGap_nonneg_of_le, decisionLearning_from_onlineToBatch, decisionLearning_td_error_after_update, decisionLearning_capacity_bridge_exists, decisionLearning_vc_witness, decisionLearning_pac_constant_exists |
| MLTheory.Applications.AI.Generalization | MLTheory/Applications/AI/Generalization.lean | AI | native | applications | tool | proved | AIGeneralizationScenario, deploymentGap, deploymentGap_nonneg_of_le, ai_generalization_from_onlineToBatch, ai_pac_constant_exists |
| MLTheory.Applications.LLM | MLTheory/Applications/LLM.lean | LLM | native | applications | bridge | statement |  |
| MLTheory.Applications.LLM.AlignmentObjectives | MLTheory/Applications/LLM/AlignmentObjectives.lean | LLM | native | applications | tool | proved | AlignmentObjective, preferenceMargin, preferenceMargin_nonneg_of_le, alignmentPenalty, alignedScore, alignedScore_le_objectiveScore, AlignmentScenario, alignment_pac_constant_exists |
| MLTheory.Applications.LLM.Autoregressive | MLTheory/Applications/LLM/Autoregressive.lean | LLM | native | applications | tool | proved | AutoregressiveModel, sequenceScore, autoregressiveRiskGap, AutoregressiveScenario, autoregressive_pac_constant_exists |
| MLTheory.Applications.LLM.Sampling | MLTheory/Applications/LLM/Sampling.lean | LLM | native | applications | tool | proved | SamplingPolicy, sampledToken, samplingStepScore, sequenceScore_singleton_sampled, samplingRiskGap, samplingRiskGap_nonneg_of_le, SamplingScenario, sampling_pac_constant_exists |
| MLTheory.Applications.Learning | MLTheory/Applications/Learning.lean | Learning | native | applications | bridge | statement |  |
| MLTheory.Applications.RL | MLTheory/Applications/RL.lean | RL | native | applications | bridge | statement |  |
| MLTheory.Books.FoML2 | MLTheory/Books/FoML2.lean | Learning | books | books | compat | statement |  |
| MLTheory.Books.SuttonBartoRL2 | MLTheory/Books/SuttonBartoRL2.lean | RL | books | books | compat | statement |  |
| MLTheory.Core | MLTheory/Core.lean | Architecture | native | core | bridge | statement |  |
| MLTheory.Core.Learning | MLTheory/Core/Learning.lean | Learning | native | core | bridge | statement |  |
| MLTheory.Core.Learning.Capacity | MLTheory/Core/Learning/Capacity.lean | Learning | native | core | tool | proved | CapacityBridge, vcDimensionBound, rademacherBound |
| MLTheory.Core.Learning.FunctionClass | MLTheory/Core/Learning/FunctionClass.lean | Learning | native | core | canonical | proved | HypothesisClass |
| MLTheory.Core.Learning.PAC | MLTheory/Core/Learning/PAC.lean | Learning | native | core | canonical | proved | PACProblem |
| MLTheory.Core.Probability | MLTheory/Core/Probability.lean | Probability | native | core | bridge | statement |  |
| MLTheory.Core.Probability.BasicMeasure | MLTheory/Core/Probability/BasicMeasure.lean | Probability | native | core | tool | proved | isMeasurableEvent, eventMass, eventMass_mono, eventMass_union_le, conditionedEvent_mass_le_left, conditionedEvent_mass_le_right |
| MLTheory.Core.Probability.Conditioning | MLTheory/Core/Probability/Conditioning.lean | Probability | native | core | tool | proved | conditionedEvent, conditionedEvent_subset_left, condWeight_nonneg |
| MLTheory.Core.Probability.ProbIneq | MLTheory/Core/Probability/ProbIneq.lean | Probability | native | core | tool | proved | tailUpperEnvelope, tailUpperEnvelope_trans, tailUpperEnvelope_add, scale_nonneg |
| MLTheory.Core.RL | MLTheory/Core/RL.lean | RL | native | core | bridge | statement |  |
| MLTheory.Core.RL.MDP | MLTheory/Core/RL/MDP.lean | RL | native | core | tool | statement | FiniteMDP, DeterministicPolicy, bellmanExpectationSpec, bellmanOptimalitySpec |
| MLTheory.Core.Statistics | MLTheory/Core/Statistics.lean | Statistics | native | core | bridge | statement |  |
| MLTheory.Core.Statistics.Information | MLTheory/Core/Statistics/Information.lean | Statistics | native | core | tool | proved | InformationPair, klSurrogate, klSurrogate_nonneg_of_le, MaxEntropyTemplate, maxEntGap, conditionalMaxEntGap |
| MLTheory.Core.Statistics.Risk | MLTheory/Core/Statistics/Risk.lean | Statistics | native | core | tool | proved | RiskPair, excessRisk, excessRisk_nonneg_of_le, excessRisk_add_empirical |
| MLTheory.Methods | MLTheory/Methods.lean | Architecture | native | methods | bridge | statement |  |
| MLTheory.Methods.Bandits | MLTheory/Methods/Bandits.lean | Bandits | native | methods | bridge | statement |  |
| MLTheory.Methods.Bandits.Adversarial | MLTheory/Methods/Bandits/Adversarial.lean | Bandits | native | methods | tool | proved | AdversarialBanditModel, adversarialRoundRegret, adversarialRoundRegret_nonneg_of_le, adversarialCumulativeRegret, adversarialCumulativeRegret_nonneg, exp3LearningRate, exp3LearningRate_nonneg, adversarialScalarCumulativeRegret, adversarialScalarCumulativeRegret_eq_foundation |
| MLTheory.Methods.Bandits.BestArmIdentification | MLTheory/Methods/Bandits/BestArmIdentification.lean | Bandits | native | methods | tool | proved | BAIProblem, simpleRegret, simpleRegret_nonneg_of_le, simpleRegret_self, cumulativeSimpleRegret, cumulativeSimpleRegret_nonneg, fixedConfidenceSampleComplexity, fixedConfidenceSampleComplexity_nonneg |
| MLTheory.Methods.Bandits.ContextualLinear | MLTheory/Methods/Bandits/ContextualLinear.lean | Bandits | native | methods | tool | proved | ContextualLinearBanditProblem, LinearScorer, predictedReward, optimisticScore, optimisticScore_ge_predicted, contextualRoundRegret, contextualRoundRegret_nonneg_of_le, contextualCumulativeRegret, contextualCumulativeRegret_nonneg, confidenceRadius, confidenceRadius_nonneg |
| MLTheory.Methods.Bandits.Dueling | MLTheory/Methods/Bandits/Dueling.lean | Bandits | native | methods | tool | proved | DuelingBanditProblem, duelAdvantage, duelAdvantage_swap_neg, duelingRegret, duelingRegret_nonneg_of_le, cumulativeDuelingRegret, cumulativeDuelingRegret_nonneg, preferenceMargin, preferenceMargin_nonneg_of_le |
| MLTheory.Methods.Bandits.Foundations | MLTheory/Methods/Bandits/Foundations.lean | Bandits | native | methods | canonical | proved | BanditInstance, regret, regret_nonneg_of_le, cumulativeRegret, cumulativeRegret_nonneg |
| MLTheory.Methods.Bandits.InformationTheory | MLTheory/Methods/Bandits/InformationTheory.lean | Bandits | native | methods | tool | proved | InformationBanditModel, klStyleBonus, klStyleBonus_nonneg, informationRegret, informationRegret_nonneg_of_le, informationCumulativeRegret, informationCumulativeRegret_nonneg, informationRegret_eq_stochasticPseudoRegret |
| MLTheory.Methods.Bandits.LargeActionSpaces | MLTheory/Methods/Bandits/LargeActionSpaces.lean | Bandits | native | methods | tool | proved | LargeActionBanditProblem, actionPoolSize, actionPoolSize_nonneg, explorationBudget, candidateApproximationGap, candidateApproximationGap_nonneg_of_le, largeActionCumulativeRegret, largeActionCumulativeRegret_nonneg |
| MLTheory.Methods.Bandits.PureExplorationLinear | MLTheory/Methods/Bandits/PureExplorationLinear.lean | Bandits | native | methods | tool | proved | PureExplorationLinearProblem, estimationError, estimationError_nonneg, confidenceRadiusPE, confidenceRadiusPE_nonneg, pureExplorationSimpleRegret, pureExplorationSimpleRegret_nonneg_of_le, fixedConfidenceSampleComplexityPE, fixedConfidenceSampleComplexityPE_nonneg |
| MLTheory.Methods.Bandits.RLBridge | MLTheory/Methods/Bandits/RLBridge.lean | Bandits | native | methods | tool | proved | BanditRLBridgeProblem, banditValueGap, tdErrorProxy, banditValueGap_eq_tdErrorProxy, banditToRLCumulativeGap, banditToRLCumulativeGap_nonneg, banditTdUpdate, banditTdError_after_update |
| MLTheory.Methods.Bandits.Stochastic | MLTheory/Methods/Bandits/Stochastic.lean | Bandits | native | methods | tool | proved | StochasticBanditModel, ucbBonus, ucbScore, ucbBonus_nonneg, ucbScore_ge_empiricalMean, etcExplorationRounds, stochasticPseudoRegret, stochasticPseudoRegret_nonneg |
| MLTheory.Methods.Learning | MLTheory/Methods/Learning.lean | Learning | native | methods | bridge | statement |  |
| MLTheory.Methods.Learning.AdvancedSLT | MLTheory/Methods/Learning/AdvancedSLT.lean | Learning | native | methods | tool | proved | AdvancedSLTProblem, advancedExcessRisk, complexityPenalty, advancedExcessRiskBound, advancedExcessRisk_le_bound, sampleComplexityProxy |
| MLTheory.Methods.Learning.AutomataLanguage | MLTheory/Methods/Learning/AutomataLanguage.lean | Learning | native | methods | tool | proved | AutomataLanguageProblem, runState, accepts, zeroOneLoss, languageEmpiricalRisk, languageRiskGap |
| MLTheory.Methods.Learning.Capacity | MLTheory/Methods/Learning/Capacity.lean | Learning | native | methods | tool | proved | CapacityMethodBundle, jlDistortionGap, jlDistortionGap_nonneg_of_le, method_vcDimensionBound, method_rademacherBound, capacity_tailUpperEnvelope_refl |
| MLTheory.Methods.Learning.ConcentrationPackaging | MLTheory/Methods/Learning/ConcentrationPackaging.lean | Learning | native | methods | canonical | proved | FiniteClassConcentrationBundle, subgaussianTailENN |
| MLTheory.Methods.Learning.Contraction | MLTheory/Methods/Learning/Contraction.lean | Learning | native | methods | tool | proved | OneLipschitzAtZero, lip_contraction_abs, lip_contraction_std |
| MLTheory.Methods.Learning.DiscreteModeling | MLTheory/Methods/Learning/DiscreteModeling.lean | Learning | native | methods | tool | proved | DiscreteModelingProblem, discretePointLoss, discreteEmpiricalRisk, DiscreteComparator, discreteRiskGap, averageDiscreteRiskGap |
| MLTheory.Methods.Learning.GeneralizationTools | MLTheory/Methods/Learning/GeneralizationTools.lean | Learning | native | methods | canonical | proved | pac_badEvent_uniform_bound, pac_badEvent_union_bound |
| MLTheory.Methods.Learning.KernelBayes | MLTheory/Methods/Learning/KernelBayes.lean | Learning | native | methods | tool | proved | KernelBayesProblem, posteriorWeightUnnormalized, posteriorNormalization, posteriorWeight, kernelBayesPredictiveMean, kernelBayesRiskGap |
| MLTheory.Methods.Learning.KernelMethods | MLTheory/Methods/Learning/KernelMethods.lean | Learning | native | methods | tool | statement | KernelFunction, isPSDKernel, KernelLearningProblem, representerTheoremSpec |
| MLTheory.Methods.Learning.ModelSelection | MLTheory/Methods/Learning/ModelSelection.lean | Learning | native | methods | tool | proved | ModelSelectionProblem, structuralRiskMinimizationBound |
| MLTheory.Methods.Learning.Rademacher | MLTheory/Methods/Learning/Rademacher.lean | Learning | native | methods | canonical | proved | radStd, radAbs |
| MLTheory.Methods.Learning.SVM | MLTheory/Methods/Learning/SVM.lean | Learning | native | methods | tool | proved | BinaryClassificationDataset, boolLabelToSign, hingeLoss, svmPrimalGuarantee, svmDualGuarantee |
| MLTheory.Methods.Learning.Sequential | MLTheory/Methods/Learning/Sequential.lean | Learning | native | methods | tool | proved | SequentialLearningProblem, sequentialInstantLoss, sequentialPrefixRegret, averagePrefixRegret, sequentialRegretFromOCO, sequentialRegretFromOCO_eq_prefix |
| MLTheory.Methods.Learning.StoneWeierstrassBridge | MLTheory/Methods/Learning/StoneWeierstrassBridge.lean | Learning | native | methods | canonical | proved | stone_exists_uniform_near, stone_closure_eq_top |
| MLTheory.Methods.OCO | MLTheory/Methods/OCO.lean | OCO | native | methods | bridge | statement |  |
| MLTheory.Methods.OCO.BanditConvex | MLTheory/Methods/OCO/BanditConvex.lean | OCO | native | methods | tool | proved | BanditConvexProblem, estimationGap, trueInstantRegret, instantRegretGap, cumulativeRegretGap, banditCumulativeRegret_nonneg_of_le |
| MLTheory.Methods.OCO.Boosting | MLTheory/Methods/OCO/Boosting.lean | OCO | native | methods | tool | proved | BoostingRound, weightedExpertLoss, boostingInstantRegret, boostingCumulativeRegret, expWeightUpdate, boostingRegretFromOCO |
| MLTheory.Methods.OCO.DynamicRegret | MLTheory/Methods/OCO/DynamicRegret.lean | OCO | native | methods | tool | proved | DynamicComparator, dynamicInstantRegret, dynamicCumulativeRegret, dynamicCumulativeRegret_nonneg_of_le, staticToDynamicComparator, dynamicCumulativeRegret_eq_static |
| MLTheory.Methods.OCO.GamesAndDuality | MLTheory/Methods/OCO/GamesAndDuality.lean | OCO | native | methods | tool | proved | GameProblem, SaddleComparator, gameInstantRegret, gameCumulativeRegret, dualityGap, averageGameRegret |
| MLTheory.Methods.OCO.Generalization | MLTheory/Methods/OCO/Generalization.lean | OCO | native | methods | tool | proved | averageRegret, averageRegret_nonneg_of_le, onlineToBatch_bridge_statement, oco_pacSampleComplexityBound |
| MLTheory.Methods.OCO.OptimizationCore | MLTheory/Methods/OCO/OptimizationCore.lean | OCO | native | methods | tool | proved | OCOProblem, Comparator, OnlineUpdate, instantRegret, cumulativeRegret, instantRegret_nonneg_of_le, cumulativeRegret_nonneg_of_le, instantRegret_eq_objectiveGap |
| MLTheory.Methods.OR | MLTheory/Methods/OR.lean | OR | native | methods | bridge | statement |  |
| MLTheory.Methods.OR.ConvexCore | MLTheory/Methods/OR/ConvexCore.lean | OR | native | methods | tool | proved | ConvexObjective, FeasibleSet, objectiveGap, objectiveGap_nonneg_of_le, scaled_objectiveGap_nonneg |
| MLTheory.Methods.OR.DiscreteOptimization | MLTheory/Methods/OR/DiscreteOptimization.lean | OR | native | methods | tool | proved | DiscreteOptimizationProblem, feasibleCandidates, discreteObjectiveGap, discreteObjectiveGap_nonneg_of_le, cumulativeDiscreteObjectiveGap, cumulativeDiscreteObjectiveGap_nonneg |
| MLTheory.Methods.OR.GraphOptimization | MLTheory/Methods/OR/GraphOptimization.lean | OR | native | methods | tool | proved | GraphOptimizationProblem, pathCost, pathObjectiveGap, pathObjectiveGap_nonneg_of_le, cutObjectiveGap, cumulativePathObjectiveGap_nonneg |
| MLTheory.Methods.OR.StochasticMatrix | MLTheory/Methods/OR/StochasticMatrix.lean | OR | native | methods | tool | proved | StochasticMatrixProblem, rowMass, rowMassGap, rowMassGap_nonneg_of_le, entrywiseDeviation, cumulativeRowMassGap_nonneg |
| MLTheory.Methods.RL | MLTheory/Methods/RL.lean | RL | native | methods | bridge | statement |  |
| MLTheory.Methods.RL.DynamicProgramming | MLTheory/Methods/RL/DynamicProgramming.lean | RL | native | methods | tool | statement | valueIterationUpdate, policyEvaluationSpec, policyImprovementSpec, policyIterationConvergenceSpec |
| MLTheory.Methods.RL.MDP | MLTheory/Methods/RL/MDP.lean | RL | native | methods | tool | proved | MDPMethodProblem, bellmanOperator, valueIterationUpdate_eq_bellmanOperator, bellmanBridgeSpec |
| MLTheory.Methods.RL.TemporalDifference | MLTheory/Methods/RL/TemporalDifference.lean | RL | native | methods | tool | proved | TemporalDifferenceProblem, tdTarget, tdError, tdUpdate, tdError_after_update, tdError_sq_nonneg |

## Full list of planning modules(Not yet landed)
| module_path | target_node | source_track | status | reason |
|---|---|---|---|---|
| MLTheory.Books.BanditAlgorithms | Bandits | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartIII_AdversarialBandits | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartII_StochasticBandits | Bandits | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartIV_ContextualLinearBandits | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartI_Foundations | Bandits | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartVII_ReinforcementLearning | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartVI_PureExploration | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartV_LargeActionSpaces | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5 | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch01_MeasureTheory | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch02_ProbabilityTheory | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch03_IndependenceExpectations | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch04_LimitTheorems | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch05_PoissonApproximation | Probability | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch06_MarkovChains | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch07_Martingales | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch08_BrownianMotion | Probability | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch09_StationaryProcesses | Probability | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch10_CTMC | Probability | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch11_ErgodicTheorems | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2 | OCO | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2.PartIII_GeneralizationAndAdaptivity | OCO | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2.PartII_BanditAndGames | OCO | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2.PartIV_BoostingAndApproachability | OCO | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2.PartI_Core | OCO | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.SuttonBartoRL2.PartIII_LookingDeeper | RL | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.SuttonBartoRL2.PartII_ApproximateMethods | RL | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.SuttonBartoRL2.PartI_TabularMethods | RL | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch01_Refresher | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch02_IndependentSums | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch03_RandomVectors | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch04_RandomMatrices | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch05_WithoutIndependence | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch06_QuadraticSymmContraction | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch07_RandomProcesses | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch08_Chaining | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch09_MatrixDeviations | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.Brownian | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.CLTBridge | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.CTMC | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.DensityCDF | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.Ergodic | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.LimitLaws | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.MarkovKernels | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.Martingales | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.Moments | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.PoissonApprox | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.Stationary | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.CaseStudies | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.EligibilityTraces | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.Frontiers | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.FunctionApproximation | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.ModelBasedPlanning | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.MonteCarlo | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.NeuroscienceBridge | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.OffPolicy | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.PolicyGradient | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.PsychologyBridge | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |

## Structural Risks and Refactoring Priorities(automatic recognition)
| issue_id | severity | title | evidence | action | acceptance_gate |
|---|---|---|---|---|---|
| S4 | P2 | The key entry statement is already in,But the proof status is still statement | 3 modules;Example:MLTheory.Core.RL.MDP, MLTheory.Methods.Learning.KernelMethods, MLTheory.Methods.RL.DynamicProgramming | according to canonical_specs Prioritize statement The entrance is advanced in batches to proved;First complement dependency closure shortest link. | canonical/tool of proved Ratio increases by batch,and canonical_contract keep passing. |

## Reproducible acceptance command(After refactoring, run at least these)
```bash
python3 tools/docs/validate_ssot.py
python3 tools/docs/sync_docs.py --check
python3 tools/ci/check_taxonomy_contract.py
python3 tools/ci/check_namespace_layout.py
python3 tools/ci/check_tool_forest_consistency.py
python3 tools/ci/check_review_views_consistency.py
python3 tools/ci/check_registry_reference_hygiene.py
python3 tools/ci/check_ready_to_remove.py
bash tools/ci/check_ssot_migration_idempotent.sh
bash tools/ci/check_layer_imports.sh
bash tools/ci/check_no_new_deprecated_imports.sh
bash tools/ci/check_canonical_contract.sh
bash tools/ci/check_official_workflow_alignment.sh
bash tools/ci/check_placeholder_policy.sh
bash tools/ci/check_no_sorry_axiom.sh
~/.elan/bin/lake build
bash /Users/xiongjiangkai/xjk_papers/paper-template/scripts/formalization_preflight.sh --mode augmented
bash /Users/xiongjiangkai/xjk_papers/paper-template/scripts/check_final_signature.sh
```

## Give GPT5.2pro Suggested reading order for
1. Read 'architectural contract' and 'Phase-0 review snapshot' first to confirm hard constraints.
2. Then read 'completed implementation trajectory' and the full real-module list to avoid duplication.
3. Finally read 'planning modules + structural risk' to decide rewrite scope and migration strategy.
