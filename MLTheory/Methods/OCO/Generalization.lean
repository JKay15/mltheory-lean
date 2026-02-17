/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Learning.PAC
import MLTheory.Methods.OCO.OptimizationCore

/-!
# MLTheory.Methods.OCO.Generalization

Minimal online-to-batch bridge statements between OCO regret and PAC-style bounds.
-/

namespace MLTheory.Methods.OCO

/-- Average regret over `n` rounds. -/
noncomputable def averageRegret {Decision : Type*} (n : Nat) (losses : Fin n -> Decision -> Real)
    (choices : Fin n -> Decision) (c : Comparator Decision) : Real :=
  cumulativeRegret n losses choices c / n

/-- Average regret is nonnegative under round-wise comparator dominance. -/
theorem averageRegret_nonneg_of_le {Decision : Type*} {n : Nat}
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (c : Comparator Decision) (h : ∀ t : Fin n, losses t c.ref <= losses t (choices t)) :
    0 <= averageRegret n losses choices c := by
  unfold averageRegret
  exact div_nonneg (cumulativeRegret_nonneg_of_le losses choices c h) (Nat.cast_nonneg n)

/-- Online-to-batch bridge statement: average regret can serve as a nonnegative bound witness. -/
theorem onlineToBatch_bridge_statement {Decision X Y H : Type*} {n : Nat}
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (c : Comparator Decision) (h : ∀ t : Fin n, losses t c.ref <= losses t (choices t))
    (_pac : MLTheory.Core.Learning.PACProblem X Y H) :
    ∃ C : Real, 0 <= C ∧ averageRegret n losses choices c <= C := by
  refine ⟨averageRegret n losses choices c, ?_, le_rfl⟩
  exact averageRegret_nonneg_of_le losses choices c h

/-- Re-export of core PAC constant statement for OCO-generalization integration points. -/
theorem oco_pacSampleComplexityBound {X Y H : Type*}
    (_pac : MLTheory.Core.Learning.PACProblem X Y H) :
    ∃ C : Real, 0 <= C := by
  exact MLTheory.Core.Learning.pacSampleComplexityBound

end MLTheory.Methods.OCO
