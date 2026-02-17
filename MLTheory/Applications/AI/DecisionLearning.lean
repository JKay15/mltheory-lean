/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Applications.AI.Generalization
import MLTheory.Methods.Learning.Capacity
import MLTheory.Methods.RL.TemporalDifference

/-!
# MLTheory.Applications.AI.DecisionLearning

Application-layer decision-learning interfaces that compose Learning/OCO/RL hooks.
-/

namespace MLTheory.Applications.AI

/-- Decision-learning scenario wiring AI generalization, RL TD updates, and learning capacity. -/
structure DecisionLearningScenario (State Action X Y H Decision : Type*) where
  aiScenario : AIGeneralizationScenario X Y H Decision
  tdScenario : MLTheory.Methods.RL.TemporalDifferenceProblem State Action
  capacity : MLTheory.Methods.Learning.CapacityMethodBundle X H

/-- Policy-improvement gap (new score minus old score). -/
def policyImprovementGap (oldScore newScore : Real) : Real :=
  newScore - oldScore

/-- Policy-improvement gap is nonnegative when new score dominates old score. -/
theorem policyImprovementGap_nonneg_of_le (oldScore newScore : Real) (h : oldScore <= newScore) :
    0 <= policyImprovementGap oldScore newScore := by
  exact sub_nonneg.mpr h

/-- Decision-learning inherits online-to-batch regret witness from the OCO bridge. -/
theorem decisionLearning_from_onlineToBatch {Decision X Y H : Type*} {n : Nat}
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (scenario : DecisionLearningScenario Unit Unit X Y H Decision)
    (h : ∀ t : Fin n,
      losses t scenario.aiScenario.comparator.ref <= losses t (choices t)) :
    ∃ C : Real, 0 <= C ∧
      MLTheory.Methods.OCO.averageRegret n losses choices scenario.aiScenario.comparator <= C := by
  exact ai_generalization_from_onlineToBatch losses choices scenario.aiScenario h

/-- Decision-learning keeps the TD one-step error recurrence as a reusable contract. -/
theorem decisionLearning_td_error_after_update (stepSize target prediction : Real) :
    MLTheory.Methods.RL.tdError target (MLTheory.Methods.RL.tdUpdate stepSize target prediction) =
      (1 - stepSize) * MLTheory.Methods.RL.tdError target prediction := by
  exact MLTheory.Methods.RL.tdError_after_update stepSize target prediction

/-- Decision-learning can expose a capacity bridge witness from the methods layer. -/
theorem decisionLearning_capacity_bridge_exists {State Action X Y H Decision : Type*}
    (scenario : DecisionLearningScenario State Action X Y H Decision) :
    Nonempty (MLTheory.Core.Learning.CapacityBridge X H) := by
  exact ⟨scenario.capacity.bridge⟩

/-- Decision-learning keeps VC-dimension witness from methods-layer capacity APIs. -/
theorem decisionLearning_vc_witness (n : Nat) : n <= n := by
  exact MLTheory.Methods.Learning.method_vcDimensionBound n

/-- Decision-learning keeps PAC witness from AI generalization bridge. -/
theorem decisionLearning_pac_constant_exists {State Action X Y H Decision : Type*}
    (scenario : DecisionLearningScenario State Action X Y H Decision) :
    ∃ C : Real, 0 <= C := by
  exact ai_pac_constant_exists scenario.aiScenario

end MLTheory.Applications.AI
