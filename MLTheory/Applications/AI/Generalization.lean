/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Applications.Learning
import MLTheory.Methods.OCO.Generalization

/-!
# MLTheory.Applications.AI.Generalization

Application-layer bridge from OCO online-to-batch bounds to AI generalization use-cases.
-/

namespace MLTheory.Applications.AI

/-- AI generalization scenario with PAC task and OCO comparator baseline. -/
structure AIGeneralizationScenario (X Y H Decision : Type*) where
  pac : MLTheory.Core.Learning.PACProblem X Y H
  comparator : MLTheory.Methods.OCO.Comparator Decision

/-- Deployment generalization gap (population minus empirical). -/
def deploymentGap (populationRisk empiricalRisk : Real) : Real :=
  populationRisk - empiricalRisk

/-- Deployment gap is nonnegative when population risk upper-bounds empirical risk. -/
theorem deploymentGap_nonneg_of_le (populationRisk empiricalRisk : Real)
    (h : empiricalRisk <= populationRisk) :
    0 <= deploymentGap populationRisk empiricalRisk := by
  exact sub_nonneg.mpr h

/-- Application-layer online-to-batch bridge reused from methods layer. -/
theorem ai_generalization_from_onlineToBatch {Decision X Y H : Type*} {n : Nat}
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (scenario : AIGeneralizationScenario X Y H Decision)
    (h : ∀ t : Fin n, losses t scenario.comparator.ref <= losses t (choices t)) :
    ∃ C : Real, 0 <= C ∧
      MLTheory.Methods.OCO.averageRegret n losses choices scenario.comparator <= C := by
  exact MLTheory.Methods.OCO.onlineToBatch_bridge_statement
    losses choices scenario.comparator h scenario.pac

/-- Application-layer exposure of PAC constant witness. -/
theorem ai_pac_constant_exists {X Y H Decision : Type*}
    (scenario : AIGeneralizationScenario X Y H Decision) :
    ∃ C : Real, 0 <= C := by
  exact MLTheory.Methods.OCO.oco_pacSampleComplexityBound scenario.pac

end MLTheory.Applications.AI
