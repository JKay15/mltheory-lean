/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory
import MLTheory.Core.Learning.PAC
import MLTheory.Methods.Learning.SVM
import MLTheory.Methods.Learning.ConcentrationPackaging
import MLTheory.Applications.Learning
import MLTheory.Applications.AI
import MLTheory.Applications.LLM
import MLTheory.Core.Probability
import MLTheory.Core.Statistics
import MLTheory.Methods.Bandits
import MLTheory.Methods.OCO
import MLTheory.Methods.OR
import MLTheory.Books.FoML2

/-!
# Import Smoke

Compile-time smoke checks for both layered and legacy compatibility imports.
-/

#check MLTheory.Core.Learning.PACProblem
#check MLTheory.Methods.Learning.jlDistortionGap
#check MLTheory.Methods.Learning.advancedExcessRiskBound
#check MLTheory.Methods.Learning.languageRiskGap
#check MLTheory.Methods.Learning.discreteRiskGap
#check MLTheory.Methods.Learning.sequentialPrefixRegret
#check MLTheory.Methods.Learning.kernelBayesRiskGap
#check MLTheory.Methods.Learning.hingeLoss
#check MLTheory.Methods.RL.valueIterationUpdate
#check MLTheory.Methods.RL.MDPMethodProblem
#check MLTheory.Methods.RL.tdError_after_update
#check MLTheory.Applications.AI.ai_pac_constant_exists
#check MLTheory.Applications.AI.decisionLearning_pac_constant_exists
#check MLTheory.Applications.LLM.autoregressive_pac_constant_exists
#check MLTheory.Applications.LLM.sampling_pac_constant_exists
#check MLTheory.Applications.LLM.alignment_pac_constant_exists
#check MLTheory.Methods.Learning.svmDualGuarantee
#check MLTheory.Core.Probability.conditionedEvent
#check MLTheory.Core.Probability.tailUpperEnvelope
#check MLTheory.Core.Probability.eventMass
#check MLTheory.Core.Statistics.excessRisk
#check MLTheory.Core.Statistics.klSurrogate
#check MLTheory.Methods.OR.objectiveGap
#check MLTheory.Methods.OR.discreteObjectiveGap
#check MLTheory.Methods.OR.pathObjectiveGap
#check MLTheory.Methods.OR.rowMassGap
#check MLTheory.Methods.Bandits.cumulativeRegret
#check MLTheory.Methods.Bandits.ucbScore
#check MLTheory.Methods.Bandits.klStyleBonus
#check MLTheory.Methods.Bandits.exp3LearningRate
#check MLTheory.Methods.Bandits.simpleRegret
#check MLTheory.Methods.Bandits.contextualCumulativeRegret
#check MLTheory.Methods.Bandits.duelAdvantage
#check MLTheory.Methods.Bandits.actionPoolSize
#check MLTheory.Methods.Bandits.confidenceRadiusPE
#check MLTheory.Methods.Bandits.banditValueGap_eq_tdErrorProxy
#check MLTheory.Methods.OCO.averageRegret
#check MLTheory.Methods.OCO.cumulativeRegret
#check MLTheory.Methods.OCO.cumulativeRegretGap
#check MLTheory.Methods.OCO.dynamicCumulativeRegret
#check MLTheory.Methods.OCO.gameCumulativeRegret
#check MLTheory.Methods.OCO.boostingCumulativeRegret
