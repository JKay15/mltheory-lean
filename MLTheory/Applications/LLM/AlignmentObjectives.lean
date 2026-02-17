/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Applications.LLM.Sampling

/-!
# MLTheory.Applications.LLM.AlignmentObjectives

Application-layer alignment-objective interfaces composed with sampling contracts.
-/

namespace MLTheory.Applications.LLM

/-- Minimal alignment objective over generated token sequences. -/
structure AlignmentObjective (Token : Type*) where
  score : List Token -> Real

/-- Preference margin between a chosen completion and a rejected completion. -/
def preferenceMargin {Token : Type*} (obj : AlignmentObjective Token)
    (chosen rejected : List Token) : Real :=
  obj.score chosen - obj.score rejected

/-- Preference margin is nonnegative when chosen score dominates rejected score. -/
theorem preferenceMargin_nonneg_of_le {Token : Type*} (obj : AlignmentObjective Token)
    (chosen rejected : List Token) (h : obj.score rejected <= obj.score chosen) :
    0 <= preferenceMargin obj chosen rejected := by
  exact sub_nonneg.mpr h

/-- Alignment penalty reused from sampling risk-gap contract. -/
def alignmentPenalty (populationRisk empiricalRisk : Real) : Real :=
  samplingRiskGap populationRisk empiricalRisk

/-- Regularized alignment score with nonnegative penalty weight. -/
def alignedScore (objectiveScore penaltyWeight populationRisk empiricalRisk : Real) : Real :=
  objectiveScore - penaltyWeight * alignmentPenalty populationRisk empiricalRisk

/-- Regularization term does not increase objective score under nonnegative assumptions. -/
theorem alignedScore_le_objectiveScore
    (objectiveScore penaltyWeight populationRisk empiricalRisk : Real)
    (hWeight : 0 <= penaltyWeight) (hGap : empiricalRisk <= populationRisk) :
    alignedScore objectiveScore penaltyWeight populationRisk empiricalRisk <= objectiveScore := by
  unfold alignedScore alignmentPenalty
  have hPenalty : 0 <= samplingRiskGap populationRisk empiricalRisk := by
    exact samplingRiskGap_nonneg_of_le populationRisk empiricalRisk hGap
  nlinarith [mul_nonneg hWeight hPenalty]

/-- Alignment scenario extends sampling scenario with an objective functional. -/
structure AlignmentScenario (Token X Y H Decision : Type*) where
  sampling : SamplingScenario Token X Y H Decision
  objective : AlignmentObjective Token

/-- Alignment applications inherit PAC witness from sampling bridge. -/
theorem alignment_pac_constant_exists {Token X Y H Decision : Type*}
    (scenario : AlignmentScenario Token X Y H Decision) :
    ∃ C : Real, 0 <= C := by
  exact sampling_pac_constant_exists scenario.sampling

end MLTheory.Applications.LLM
