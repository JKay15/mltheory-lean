# smallest API card(APICards)

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## How to use(2 minute)
1. Start with 'See recent changes first' and verify these items match expectations.
2. Then go to the corresponding field grouping,View by module card:do what + Which statements to look at first.
3. No need to read the entire database at once;Only spot checks in each round 3-5 Just one module.

## See recent changes first
| module_path | node | state(layer/role/proof) | Read the statement first(Top3) |
|---|---|---|---|
| MLTheory.Core.Probability.BasicMeasure | Probability | core/tool/proved | isMeasurableEvent, eventMass, eventMass_mono, ...(+3) |
| MLTheory.Methods.Learning.DiscreteModeling | Learning | methods/tool/proved | DiscreteModelingProblem, discretePointLoss, discreteEmpiricalRisk, ...(+3) |
| MLTheory.Methods.Learning.AutomataLanguage | Learning | methods/tool/proved | AutomataLanguageProblem, runState, accepts, ...(+3) |
| MLTheory.Methods.Learning.KernelBayes | Learning | methods/tool/proved | KernelBayesProblem, posteriorWeightUnnormalized, posteriorNormalization, ...(+3) |
| MLTheory.Methods.Learning.Sequential | Learning | methods/tool/proved | SequentialLearningProblem, sequentialInstantLoss, sequentialPrefixRegret, ...(+3) |
| MLTheory.Methods.Learning.AdvancedSLT | Learning | methods/tool/proved | AdvancedSLTProblem, advancedExcessRisk, complexityPenalty, ...(+3) |
| MLTheory.Methods.OCO.Boosting | OCO | methods/tool/proved | BoostingRound, weightedExpertLoss, boostingInstantRegret, ...(+3) |
| MLTheory.Methods.OCO.GamesAndDuality | OCO | methods/tool/proved | GameProblem, SaddleComparator, gameInstantRegret, ...(+3) |
| MLTheory.Methods.OCO.DynamicRegret | OCO | methods/tool/proved | DynamicComparator, dynamicInstantRegret, dynamicCumulativeRegret, ...(+3) |
| MLTheory.Methods.OCO.BanditConvex | OCO | methods/tool/proved | BanditConvexProblem, estimationGap, trueInstantRegret, ...(+3) |

## View by area(public module)

### Probability(4)
- `MLTheory.Core.Probability`:base layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Core/Probability.lean`
- [NEW] `MLTheory.Core.Probability.BasicMeasure`:base layerofTool interface;Look first `isMeasurableEvent, eventMass, eventMass_mono, ...(+3)`;state `proved`;document `MLTheory/Core/Probability/BasicMeasure.lean`
- `MLTheory.Core.Probability.Conditioning`:base layerofTool interface;Look first `conditionedEvent, conditionedEvent_subset_left, condWeight_nonneg`;state `proved`;document `MLTheory/Core/Probability/Conditioning.lean`
- `MLTheory.Core.Probability.ProbIneq`:base layerofTool interface;Look first `tailUpperEnvelope, tailUpperEnvelope_trans, tailUpperEnvelope_add, ...(+1)`;state `proved`;document `MLTheory/Core/Probability/ProbIneq.lean`

### Statistics(3)
- `MLTheory.Core.Statistics`:base layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Core/Statistics.lean`
- `MLTheory.Core.Statistics.Information`:base layerofTool interface;Look first `InformationPair, klSurrogate, klSurrogate_nonneg_of_le, ...(+3)`;state `proved`;document `MLTheory/Core/Statistics/Information.lean`
- `MLTheory.Core.Statistics.Risk`:base layerofTool interface;Look first `RiskPair, excessRisk, excessRisk_nonneg_of_le, ...(+1)`;state `proved`;document `MLTheory/Core/Statistics/Risk.lean`

### Learning(21)
- `MLTheory.Applications.Learning`:Application layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Applications/Learning.lean`
- `MLTheory.Books.FoML2`:book layerofCompatible entrance;Look first `-`;state `statement`;document `MLTheory/Books/FoML2.lean`
- `MLTheory.Core.Learning`:base layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Core/Learning.lean`
- `MLTheory.Core.Learning.Capacity`:base layerofTool interface;Look first `CapacityBridge, vcDimensionBound, rademacherBound`;state `proved`;document `MLTheory/Core/Learning/Capacity.lean`
- `MLTheory.Core.Learning.FunctionClass`:base layerofmain entrance;Look first `HypothesisClass`;state `proved`;document `MLTheory/Core/Learning/FunctionClass.lean`
- `MLTheory.Core.Learning.PAC`:base layerofmain entrance;Look first `PACProblem`;state `proved`;document `MLTheory/Core/Learning/PAC.lean`
- `MLTheory.Methods.Learning`:method layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Methods/Learning.lean`
- [NEW] `MLTheory.Methods.Learning.AdvancedSLT`:method layerofTool interface;Look first `AdvancedSLTProblem, advancedExcessRisk, complexityPenalty, ...(+3)`;state `proved`;document `MLTheory/Methods/Learning/AdvancedSLT.lean`
- [NEW] `MLTheory.Methods.Learning.AutomataLanguage`:method layerofTool interface;Look first `AutomataLanguageProblem, runState, accepts, ...(+3)`;state `proved`;document `MLTheory/Methods/Learning/AutomataLanguage.lean`
- `MLTheory.Methods.Learning.Capacity`:method layerofTool interface;Look first `CapacityMethodBundle, jlDistortionGap, jlDistortionGap_nonneg_of_le, ...(+3)`;state `proved`;document `MLTheory/Methods/Learning/Capacity.lean`
- `MLTheory.Methods.Learning.ConcentrationPackaging`:method layerofmain entrance;Look first `FiniteClassConcentrationBundle, subgaussianTailENN`;state `proved`;document `MLTheory/Methods/Learning/ConcentrationPackaging.lean`
- `MLTheory.Methods.Learning.Contraction`:method layerofTool interface;Look first `OneLipschitzAtZero, lip_contraction_abs, lip_contraction_std`;state `proved`;document `MLTheory/Methods/Learning/Contraction.lean`
- [NEW] `MLTheory.Methods.Learning.DiscreteModeling`:method layerofTool interface;Look first `DiscreteModelingProblem, discretePointLoss, discreteEmpiricalRisk, ...(+3)`;state `proved`;document `MLTheory/Methods/Learning/DiscreteModeling.lean`
- `MLTheory.Methods.Learning.GeneralizationTools`:method layerofmain entrance;Look first `pac_badEvent_uniform_bound, pac_badEvent_union_bound`;state `proved`;document `MLTheory/Methods/Learning/GeneralizationTools.lean`
- [NEW] `MLTheory.Methods.Learning.KernelBayes`:method layerofTool interface;Look first `KernelBayesProblem, posteriorWeightUnnormalized, posteriorNormalization, ...(+3)`;state `proved`;document `MLTheory/Methods/Learning/KernelBayes.lean`
- `MLTheory.Methods.Learning.KernelMethods`:method layerofTool interface;Look first `KernelFunction, isPSDKernel, KernelLearningProblem, ...(+1)`;state `statement`;document `MLTheory/Methods/Learning/KernelMethods.lean`
- `MLTheory.Methods.Learning.ModelSelection`:method layerofTool interface;Look first `ModelSelectionProblem, structuralRiskMinimizationBound`;state `proved`;document `MLTheory/Methods/Learning/ModelSelection.lean`
- `MLTheory.Methods.Learning.Rademacher`:method layerofmain entrance;Look first `radStd, radAbs`;state `proved`;document `MLTheory/Methods/Learning/Rademacher.lean`
- `MLTheory.Methods.Learning.SVM`:method layerofTool interface;Look first `BinaryClassificationDataset, boolLabelToSign, hingeLoss, ...(+2)`;state `proved`;document `MLTheory/Methods/Learning/SVM.lean`
- [NEW] `MLTheory.Methods.Learning.Sequential`:method layerofTool interface;Look first `SequentialLearningProblem, sequentialInstantLoss, sequentialPrefixRegret, ...(+3)`;state `proved`;document `MLTheory/Methods/Learning/Sequential.lean`
- `MLTheory.Methods.Learning.StoneWeierstrassBridge`:method layerofmain entrance;Look first `stone_exists_uniform_near, stone_closure_eq_top`;state `proved`;document `MLTheory/Methods/Learning/StoneWeierstrassBridge.lean`

### OR(5)
- `MLTheory.Methods.OR`:method layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Methods/OR.lean`
- `MLTheory.Methods.OR.ConvexCore`:method layerofTool interface;Look first `ConvexObjective, FeasibleSet, objectiveGap, ...(+2)`;state `proved`;document `MLTheory/Methods/OR/ConvexCore.lean`
- `MLTheory.Methods.OR.DiscreteOptimization`:method layerofTool interface;Look first `DiscreteOptimizationProblem, feasibleCandidates, discreteObjectiveGap, ...(+3)`;state `proved`;document `MLTheory/Methods/OR/DiscreteOptimization.lean`
- [NEW] `MLTheory.Methods.OR.GraphOptimization`:method layerofTool interface;Look first `GraphOptimizationProblem, pathCost, pathObjectiveGap, ...(+3)`;state `proved`;document `MLTheory/Methods/OR/GraphOptimization.lean`
- [NEW] `MLTheory.Methods.OR.StochasticMatrix`:method layerofTool interface;Look first `StochasticMatrixProblem, rowMass, rowMassGap, ...(+3)`;state `proved`;document `MLTheory/Methods/OR/StochasticMatrix.lean`

### RL(8)
- `MLTheory.Applications.RL`:Application layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Applications/RL.lean`
- `MLTheory.Books.SuttonBartoRL2`:book layerofCompatible entrance;Look first `-`;state `statement`;document `MLTheory/Books/SuttonBartoRL2.lean`
- `MLTheory.Core.RL`:base layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Core/RL.lean`
- `MLTheory.Core.RL.MDP`:base layerofTool interface;Look first `FiniteMDP, DeterministicPolicy, bellmanExpectationSpec, ...(+1)`;state `statement`;document `MLTheory/Core/RL/MDP.lean`
- `MLTheory.Methods.RL`:method layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Methods/RL.lean`
- `MLTheory.Methods.RL.DynamicProgramming`:method layerofTool interface;Look first `valueIterationUpdate, policyEvaluationSpec, policyImprovementSpec, ...(+1)`;state `statement`;document `MLTheory/Methods/RL/DynamicProgramming.lean`
- `MLTheory.Methods.RL.MDP`:method layerofTool interface;Look first `MDPMethodProblem, bellmanOperator, valueIterationUpdate_eq_bellmanOperator, ...(+1)`;state `proved`;document `MLTheory/Methods/RL/MDP.lean`
- `MLTheory.Methods.RL.TemporalDifference`:method layerofTool interface;Look first `TemporalDifferenceProblem, tdTarget, tdError, ...(+3)`;state `proved`;document `MLTheory/Methods/RL/TemporalDifference.lean`

### OCO(7)
- `MLTheory.Methods.OCO`:method layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Methods/OCO.lean`
- [NEW] `MLTheory.Methods.OCO.BanditConvex`:method layerofTool interface;Look first `BanditConvexProblem, estimationGap, trueInstantRegret, ...(+3)`;state `proved`;document `MLTheory/Methods/OCO/BanditConvex.lean`
- [NEW] `MLTheory.Methods.OCO.Boosting`:method layerofTool interface;Look first `BoostingRound, weightedExpertLoss, boostingInstantRegret, ...(+3)`;state `proved`;document `MLTheory/Methods/OCO/Boosting.lean`
- [NEW] `MLTheory.Methods.OCO.DynamicRegret`:method layerofTool interface;Look first `DynamicComparator, dynamicInstantRegret, dynamicCumulativeRegret, ...(+3)`;state `proved`;document `MLTheory/Methods/OCO/DynamicRegret.lean`
- [NEW] `MLTheory.Methods.OCO.GamesAndDuality`:method layerofTool interface;Look first `GameProblem, SaddleComparator, gameInstantRegret, ...(+3)`;state `proved`;document `MLTheory/Methods/OCO/GamesAndDuality.lean`
- `MLTheory.Methods.OCO.Generalization`:method layerofTool interface;Look first `averageRegret, averageRegret_nonneg_of_le, onlineToBatch_bridge_statement, ...(+1)`;state `proved`;document `MLTheory/Methods/OCO/Generalization.lean`
- `MLTheory.Methods.OCO.OptimizationCore`:method layerofTool interface;Look first `OCOProblem, Comparator, OnlineUpdate, ...(+5)`;state `proved`;document `MLTheory/Methods/OCO/OptimizationCore.lean`

### Bandits(11)
- `MLTheory.Methods.Bandits`:method layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Methods/Bandits.lean`
- `MLTheory.Methods.Bandits.Adversarial`:method layerofTool interface;Look first `AdversarialBanditModel, adversarialRoundRegret, adversarialRoundRegret_nonneg_of_le, ...(+6)`;state `proved`;document `MLTheory/Methods/Bandits/Adversarial.lean`
- `MLTheory.Methods.Bandits.BestArmIdentification`:method layerofTool interface;Look first `BAIProblem, simpleRegret, simpleRegret_nonneg_of_le, ...(+5)`;state `proved`;document `MLTheory/Methods/Bandits/BestArmIdentification.lean`
- `MLTheory.Methods.Bandits.ContextualLinear`:method layerofTool interface;Look first `ContextualLinearBanditProblem, LinearScorer, predictedReward, ...(+8)`;state `proved`;document `MLTheory/Methods/Bandits/ContextualLinear.lean`
- `MLTheory.Methods.Bandits.Dueling`:method layerofTool interface;Look first `DuelingBanditProblem, duelAdvantage, duelAdvantage_swap_neg, ...(+6)`;state `proved`;document `MLTheory/Methods/Bandits/Dueling.lean`
- `MLTheory.Methods.Bandits.Foundations`:method layerofmain entrance;Look first `BanditInstance, regret, regret_nonneg_of_le, ...(+2)`;state `proved`;document `MLTheory/Methods/Bandits/Foundations.lean`
- `MLTheory.Methods.Bandits.InformationTheory`:method layerofTool interface;Look first `InformationBanditModel, klStyleBonus, klStyleBonus_nonneg, ...(+5)`;state `proved`;document `MLTheory/Methods/Bandits/InformationTheory.lean`
- `MLTheory.Methods.Bandits.LargeActionSpaces`:method layerofTool interface;Look first `LargeActionBanditProblem, actionPoolSize, actionPoolSize_nonneg, ...(+5)`;state `proved`;document `MLTheory/Methods/Bandits/LargeActionSpaces.lean`
- `MLTheory.Methods.Bandits.PureExplorationLinear`:method layerofTool interface;Look first `PureExplorationLinearProblem, estimationError, estimationError_nonneg, ...(+6)`;state `proved`;document `MLTheory/Methods/Bandits/PureExplorationLinear.lean`
- `MLTheory.Methods.Bandits.RLBridge`:method layerofTool interface;Look first `BanditRLBridgeProblem, banditValueGap, tdErrorProxy, ...(+5)`;state `proved`;document `MLTheory/Methods/Bandits/RLBridge.lean`
- `MLTheory.Methods.Bandits.Stochastic`:method layerofTool interface;Look first `StochasticBanditModel, ucbBonus, ucbScore, ...(+5)`;state `proved`;document `MLTheory/Methods/Bandits/Stochastic.lean`

### AI(3)
- `MLTheory.Applications.AI`:Application layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Applications/AI.lean`
- `MLTheory.Applications.AI.DecisionLearning`:Application layerofTool interface;Look first `DecisionLearningScenario, policyImprovementGap, policyImprovementGap_nonneg_of_le, ...(+5)`;state `proved`;document `MLTheory/Applications/AI/DecisionLearning.lean`
- `MLTheory.Applications.AI.Generalization`:Application layerofTool interface;Look first `AIGeneralizationScenario, deploymentGap, deploymentGap_nonneg_of_le, ...(+2)`;state `proved`;document `MLTheory/Applications/AI/Generalization.lean`

### LLM(4)
- `MLTheory.Applications.LLM`:Application layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Applications/LLM.lean`
- `MLTheory.Applications.LLM.AlignmentObjectives`:Application layerofTool interface;Look first `AlignmentObjective, preferenceMargin, preferenceMargin_nonneg_of_le, ...(+5)`;state `proved`;document `MLTheory/Applications/LLM/AlignmentObjectives.lean`
- `MLTheory.Applications.LLM.Autoregressive`:Application layerofTool interface;Look first `AutoregressiveModel, sequenceScore, autoregressiveRiskGap, ...(+2)`;state `proved`;document `MLTheory/Applications/LLM/Autoregressive.lean`
- `MLTheory.Applications.LLM.Sampling`:Application layerofTool interface;Look first `SamplingPolicy, sampledToken, samplingStepScore, ...(+5)`;state `proved`;document `MLTheory/Applications/LLM/Sampling.lean`

### Architecture(3)
- `MLTheory`:Compatibility layerofbridge interface;Look first `-`;state `statement`;document `MLTheory.lean`
- `MLTheory.Core`:base layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Core.lean`
- `MLTheory.Methods`:method layerofbridge interface;Look first `-`;state `statement`;document `MLTheory/Methods.lean`

## Spot check suggestions
1. Check first every time 1 indivual `NEW` module + 1 Old modules in the same field,Confirm whether the style is consistent.
2. If the card description is inconsistent with the code,Prioritize repair SSOT,Regenerate the document.
