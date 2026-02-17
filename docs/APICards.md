# 最小 API 卡片（APICards）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 怎么用（2 分钟）
1. 先看“最近变更优先看”，只检查这几项是否符合你的预期。
2. 再到对应领域分组，按模块卡片看：做什么 + 先看哪些声明。
3. 不需要一次看全库；每轮只抽查 3-5 个模块即可。

## 最近变更优先看
| module_path | node | 状态(layer/role/proof) | 先看声明(Top3) |
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

## 按领域查看（public 模块）

### Probability（4）
- `MLTheory.Core.Probability`：基础层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Core/Probability.lean`
- [NEW] `MLTheory.Core.Probability.BasicMeasure`：基础层的工具接口；先看 `isMeasurableEvent, eventMass, eventMass_mono, ...(+3)`；状态 `proved`；文件 `MLTheory/Core/Probability/BasicMeasure.lean`
- `MLTheory.Core.Probability.Conditioning`：基础层的工具接口；先看 `conditionedEvent, conditionedEvent_subset_left, condWeight_nonneg`；状态 `proved`；文件 `MLTheory/Core/Probability/Conditioning.lean`
- `MLTheory.Core.Probability.ProbIneq`：基础层的工具接口；先看 `tailUpperEnvelope, tailUpperEnvelope_trans, tailUpperEnvelope_add, ...(+1)`；状态 `proved`；文件 `MLTheory/Core/Probability/ProbIneq.lean`

### Statistics（3）
- `MLTheory.Core.Statistics`：基础层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Core/Statistics.lean`
- `MLTheory.Core.Statistics.Information`：基础层的工具接口；先看 `InformationPair, klSurrogate, klSurrogate_nonneg_of_le, ...(+3)`；状态 `proved`；文件 `MLTheory/Core/Statistics/Information.lean`
- `MLTheory.Core.Statistics.Risk`：基础层的工具接口；先看 `RiskPair, excessRisk, excessRisk_nonneg_of_le, ...(+1)`；状态 `proved`；文件 `MLTheory/Core/Statistics/Risk.lean`

### Learning（21）
- `MLTheory.Applications.Learning`：应用层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Applications/Learning.lean`
- `MLTheory.Books.FoML2`：书籍层的兼容入口；先看 `—`；状态 `statement`；文件 `MLTheory/Books/FoML2.lean`
- `MLTheory.Core.Learning`：基础层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Core/Learning.lean`
- `MLTheory.Core.Learning.Capacity`：基础层的工具接口；先看 `CapacityBridge, vcDimensionBound, rademacherBound`；状态 `proved`；文件 `MLTheory/Core/Learning/Capacity.lean`
- `MLTheory.Core.Learning.FunctionClass`：基础层的主入口；先看 `HypothesisClass`；状态 `proved`；文件 `MLTheory/Core/Learning/FunctionClass.lean`
- `MLTheory.Core.Learning.PAC`：基础层的主入口；先看 `PACProblem`；状态 `proved`；文件 `MLTheory/Core/Learning/PAC.lean`
- `MLTheory.Methods.Learning`：方法层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Methods/Learning.lean`
- [NEW] `MLTheory.Methods.Learning.AdvancedSLT`：方法层的工具接口；先看 `AdvancedSLTProblem, advancedExcessRisk, complexityPenalty, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/Learning/AdvancedSLT.lean`
- [NEW] `MLTheory.Methods.Learning.AutomataLanguage`：方法层的工具接口；先看 `AutomataLanguageProblem, runState, accepts, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/Learning/AutomataLanguage.lean`
- `MLTheory.Methods.Learning.Capacity`：方法层的工具接口；先看 `CapacityMethodBundle, jlDistortionGap, jlDistortionGap_nonneg_of_le, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/Learning/Capacity.lean`
- `MLTheory.Methods.Learning.ConcentrationPackaging`：方法层的主入口；先看 `FiniteClassConcentrationBundle, subgaussianTailENN`；状态 `proved`；文件 `MLTheory/Methods/Learning/ConcentrationPackaging.lean`
- `MLTheory.Methods.Learning.Contraction`：方法层的工具接口；先看 `OneLipschitzAtZero, lip_contraction_abs, lip_contraction_std`；状态 `proved`；文件 `MLTheory/Methods/Learning/Contraction.lean`
- [NEW] `MLTheory.Methods.Learning.DiscreteModeling`：方法层的工具接口；先看 `DiscreteModelingProblem, discretePointLoss, discreteEmpiricalRisk, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/Learning/DiscreteModeling.lean`
- `MLTheory.Methods.Learning.GeneralizationTools`：方法层的主入口；先看 `pac_badEvent_uniform_bound, pac_badEvent_union_bound`；状态 `proved`；文件 `MLTheory/Methods/Learning/GeneralizationTools.lean`
- [NEW] `MLTheory.Methods.Learning.KernelBayes`：方法层的工具接口；先看 `KernelBayesProblem, posteriorWeightUnnormalized, posteriorNormalization, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/Learning/KernelBayes.lean`
- `MLTheory.Methods.Learning.KernelMethods`：方法层的工具接口；先看 `KernelFunction, isPSDKernel, KernelLearningProblem, ...(+1)`；状态 `proved`；文件 `MLTheory/Methods/Learning/KernelMethods.lean`
- `MLTheory.Methods.Learning.ModelSelection`：方法层的工具接口；先看 `ModelSelectionProblem, structuralRiskMinimizationBound`；状态 `proved`；文件 `MLTheory/Methods/Learning/ModelSelection.lean`
- `MLTheory.Methods.Learning.Rademacher`：方法层的主入口；先看 `radStd, radAbs`；状态 `proved`；文件 `MLTheory/Methods/Learning/Rademacher.lean`
- `MLTheory.Methods.Learning.SVM`：方法层的工具接口；先看 `BinaryClassificationDataset, boolLabelToSign, hingeLoss, ...(+2)`；状态 `proved`；文件 `MLTheory/Methods/Learning/SVM.lean`
- [NEW] `MLTheory.Methods.Learning.Sequential`：方法层的工具接口；先看 `SequentialLearningProblem, sequentialInstantLoss, sequentialPrefixRegret, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/Learning/Sequential.lean`
- `MLTheory.Methods.Learning.StoneWeierstrassBridge`：方法层的主入口；先看 `stone_exists_uniform_near, stone_closure_eq_top`；状态 `proved`；文件 `MLTheory/Methods/Learning/StoneWeierstrassBridge.lean`

### OR（5）
- `MLTheory.Methods.OR`：方法层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Methods/OR.lean`
- `MLTheory.Methods.OR.ConvexCore`：方法层的工具接口；先看 `ConvexObjective, FeasibleSet, objectiveGap, ...(+2)`；状态 `proved`；文件 `MLTheory/Methods/OR/ConvexCore.lean`
- `MLTheory.Methods.OR.DiscreteOptimization`：方法层的工具接口；先看 `DiscreteOptimizationProblem, feasibleCandidates, discreteObjectiveGap, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/OR/DiscreteOptimization.lean`
- [NEW] `MLTheory.Methods.OR.GraphOptimization`：方法层的工具接口；先看 `GraphOptimizationProblem, pathCost, pathObjectiveGap, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/OR/GraphOptimization.lean`
- [NEW] `MLTheory.Methods.OR.StochasticMatrix`：方法层的工具接口；先看 `StochasticMatrixProblem, rowMass, rowMassGap, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/OR/StochasticMatrix.lean`

### RL（8）
- `MLTheory.Applications.RL`：应用层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Applications/RL.lean`
- `MLTheory.Books.SuttonBartoRL2`：书籍层的兼容入口；先看 `—`；状态 `statement`；文件 `MLTheory/Books/SuttonBartoRL2.lean`
- `MLTheory.Core.RL`：基础层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Core/RL.lean`
- `MLTheory.Core.RL.MDP`：基础层的工具接口；先看 `FiniteMDP, DeterministicPolicy, bellmanExpectationPlaceholder, ...(+1)`；状态 `proved`；文件 `MLTheory/Core/RL/MDP.lean`
- `MLTheory.Methods.RL`：方法层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Methods/RL.lean`
- `MLTheory.Methods.RL.DynamicProgramming`：方法层的工具接口；先看 `valueIterationUpdate, policyEvaluationPlaceholder, policyImprovementPlaceholder, ...(+1)`；状态 `proved`；文件 `MLTheory/Methods/RL/DynamicProgramming.lean`
- `MLTheory.Methods.RL.MDP`：方法层的工具接口；先看 `MDPMethodProblem, bellmanOperator, valueIterationUpdate_eq_bellmanOperator, ...(+1)`；状态 `proved`；文件 `MLTheory/Methods/RL/MDP.lean`
- `MLTheory.Methods.RL.TemporalDifference`：方法层的工具接口；先看 `TemporalDifferenceProblem, tdTarget, tdError, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/RL/TemporalDifference.lean`

### OCO（7）
- `MLTheory.Methods.OCO`：方法层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Methods/OCO.lean`
- [NEW] `MLTheory.Methods.OCO.BanditConvex`：方法层的工具接口；先看 `BanditConvexProblem, estimationGap, trueInstantRegret, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/OCO/BanditConvex.lean`
- [NEW] `MLTheory.Methods.OCO.Boosting`：方法层的工具接口；先看 `BoostingRound, weightedExpertLoss, boostingInstantRegret, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/OCO/Boosting.lean`
- [NEW] `MLTheory.Methods.OCO.DynamicRegret`：方法层的工具接口；先看 `DynamicComparator, dynamicInstantRegret, dynamicCumulativeRegret, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/OCO/DynamicRegret.lean`
- [NEW] `MLTheory.Methods.OCO.GamesAndDuality`：方法层的工具接口；先看 `GameProblem, SaddleComparator, gameInstantRegret, ...(+3)`；状态 `proved`；文件 `MLTheory/Methods/OCO/GamesAndDuality.lean`
- `MLTheory.Methods.OCO.Generalization`：方法层的工具接口；先看 `averageRegret, averageRegret_nonneg_of_le, onlineToBatch_bridge_statement, ...(+1)`；状态 `proved`；文件 `MLTheory/Methods/OCO/Generalization.lean`
- `MLTheory.Methods.OCO.OptimizationCore`：方法层的工具接口；先看 `OCOProblem, Comparator, OnlineUpdate, ...(+5)`；状态 `proved`；文件 `MLTheory/Methods/OCO/OptimizationCore.lean`

### Bandits（11）
- `MLTheory.Methods.Bandits`：方法层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Methods/Bandits.lean`
- `MLTheory.Methods.Bandits.Adversarial`：方法层的工具接口；先看 `AdversarialBanditModel, adversarialRoundRegret, adversarialRoundRegret_nonneg_of_le, ...(+6)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/Adversarial.lean`
- `MLTheory.Methods.Bandits.BestArmIdentification`：方法层的工具接口；先看 `BAIProblem, simpleRegret, simpleRegret_nonneg_of_le, ...(+5)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/BestArmIdentification.lean`
- `MLTheory.Methods.Bandits.ContextualLinear`：方法层的工具接口；先看 `ContextualLinearBanditProblem, LinearScorer, predictedReward, ...(+8)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/ContextualLinear.lean`
- `MLTheory.Methods.Bandits.Dueling`：方法层的工具接口；先看 `DuelingBanditProblem, duelAdvantage, duelAdvantage_swap_neg, ...(+6)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/Dueling.lean`
- `MLTheory.Methods.Bandits.Foundations`：方法层的主入口；先看 `BanditInstance, regret, regret_nonneg_of_le, ...(+2)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/Foundations.lean`
- `MLTheory.Methods.Bandits.InformationTheory`：方法层的工具接口；先看 `InformationBanditModel, klStyleBonus, klStyleBonus_nonneg, ...(+5)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/InformationTheory.lean`
- `MLTheory.Methods.Bandits.LargeActionSpaces`：方法层的工具接口；先看 `LargeActionBanditProblem, actionPoolSize, actionPoolSize_nonneg, ...(+5)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/LargeActionSpaces.lean`
- `MLTheory.Methods.Bandits.PureExplorationLinear`：方法层的工具接口；先看 `PureExplorationLinearProblem, estimationError, estimationError_nonneg, ...(+6)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/PureExplorationLinear.lean`
- `MLTheory.Methods.Bandits.RLBridge`：方法层的工具接口；先看 `BanditRLBridgeProblem, banditValueGap, tdErrorProxy, ...(+5)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/RLBridge.lean`
- `MLTheory.Methods.Bandits.Stochastic`：方法层的工具接口；先看 `StochasticBanditModel, ucbBonus, ucbScore, ...(+5)`；状态 `proved`；文件 `MLTheory/Methods/Bandits/Stochastic.lean`

### AI（3）
- `MLTheory.Applications.AI`：应用层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Applications/AI.lean`
- `MLTheory.Applications.AI.DecisionLearning`：应用层的工具接口；先看 `DecisionLearningScenario, policyImprovementGap, policyImprovementGap_nonneg_of_le, ...(+5)`；状态 `proved`；文件 `MLTheory/Applications/AI/DecisionLearning.lean`
- `MLTheory.Applications.AI.Generalization`：应用层的工具接口；先看 `AIGeneralizationScenario, deploymentGap, deploymentGap_nonneg_of_le, ...(+2)`；状态 `proved`；文件 `MLTheory/Applications/AI/Generalization.lean`

### LLM（4）
- `MLTheory.Applications.LLM`：应用层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Applications/LLM.lean`
- `MLTheory.Applications.LLM.AlignmentObjectives`：应用层的工具接口；先看 `AlignmentObjective, preferenceMargin, preferenceMargin_nonneg_of_le, ...(+5)`；状态 `proved`；文件 `MLTheory/Applications/LLM/AlignmentObjectives.lean`
- `MLTheory.Applications.LLM.Autoregressive`：应用层的工具接口；先看 `AutoregressiveModel, sequenceScore, autoregressiveRiskGap, ...(+2)`；状态 `proved`；文件 `MLTheory/Applications/LLM/Autoregressive.lean`
- `MLTheory.Applications.LLM.Sampling`：应用层的工具接口；先看 `SamplingPolicy, sampledToken, samplingStepScore, ...(+5)`；状态 `proved`；文件 `MLTheory/Applications/LLM/Sampling.lean`

### Architecture（3）
- `MLTheory`：兼容层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory.lean`
- `MLTheory.Core`：基础层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Core.lean`
- `MLTheory.Methods`：方法层的桥接接口；先看 `—`；状态 `statement`；文件 `MLTheory/Methods.lean`

## 抽查建议
1. 每次先抽查 1 个 `NEW` 模块 + 1 个同领域旧模块，确认风格是否一致。
2. 若卡片描述与代码不一致，优先修 SSOT，再重新生成文档。
