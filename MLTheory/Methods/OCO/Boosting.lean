/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.OCO.OptimizationCore
import MLTheory.Methods.OR.ConvexCore

/-!
# MLTheory.Methods.OCO.Boosting

Minimal boosting interfaces aligned with OCO regret abstractions.
-/

namespace MLTheory.Methods.OCO

/-- Per-round expert-loss bundle used by boosting-style updates. -/
structure BoostingRound (Expert : Type*) where
  expertLoss : Expert -> Real

/-- Weighted expert loss under a boosting weight distribution. -/
def weightedExpertLoss {Expert : Type*} [Fintype Expert]
    (weights : Expert -> Real) (round : BoostingRound Expert) : Real :=
  ∑ e : Expert, weights e * round.expertLoss e

/-- Boosting one-round regret against best-reference loss. -/
def boostingInstantRegret (chosenLoss bestLoss : Real) : Real :=
  chosenLoss - bestLoss

/-- Boosting one-round regret is nonnegative when best loss is no larger. -/
theorem boostingInstantRegret_nonneg_of_le {chosenLoss bestLoss : Real}
    (h : bestLoss <= chosenLoss) :
    0 <= boostingInstantRegret chosenLoss bestLoss := by
  exact sub_nonneg.mpr h

/-- Boosting cumulative regret over a finite horizon. -/
def boostingCumulativeRegret (n : Nat)
    (chosenLosses bestLosses : Fin n -> Real) : Real :=
  ∑ t : Fin n, boostingInstantRegret (chosenLosses t) (bestLosses t)

/-- Boosting cumulative regret is nonnegative under round-wise dominance. -/
theorem boostingCumulativeRegret_nonneg_of_le {n : Nat}
    (chosenLosses bestLosses : Fin n -> Real)
    (h : ∀ t : Fin n, bestLosses t <= chosenLosses t) :
    0 <= boostingCumulativeRegret n chosenLosses bestLosses := by
  unfold boostingCumulativeRegret
  refine Finset.sum_nonneg ?_
  intro t _
  exact boostingInstantRegret_nonneg_of_le (h t)

/-- Exponential-weights style unnormalized update for one expert. -/
noncomputable def expWeightUpdate (weight learningRate lossValue : Real) : Real :=
  weight * Real.exp (-learningRate * lossValue)

/-- Exponential-weights update remains nonnegative if the old weight is nonnegative. -/
theorem expWeightUpdate_nonneg {weight learningRate lossValue : Real}
    (h : 0 <= weight) :
    0 <= expWeightUpdate weight learningRate lossValue := by
  unfold expWeightUpdate
  exact mul_nonneg h (Real.exp_pos _).le

/-- Hedge-style learning-rate template. -/
noncomputable def hedgeLearningRate (scale : Real) (horizon : Nat) : Real :=
  scale / Real.sqrt horizon

/-- Hedge learning rate is nonnegative when the scale is nonnegative. -/
theorem hedgeLearningRate_nonneg_of_nonneg {scale : Real} {horizon : Nat}
    (h : 0 <= scale) :
    0 <= hedgeLearningRate scale horizon := by
  unfold hedgeLearningRate
  exact div_nonneg h (Real.sqrt_nonneg _)

/-- Boosting instant regret is exactly OR objective gap on scalar losses. -/
theorem boostingInstantRegret_eq_objectiveGap (chosenLoss bestLoss : Real) :
    boostingInstantRegret chosenLoss bestLoss =
      MLTheory.Methods.OR.objectiveGap (fun z : Real => z) chosenLoss bestLoss := by
  rfl

/-- OCO cumulative regret can be viewed as boosting cumulative regret on scalar losses. -/
def boostingRegretFromOCO {Decision : Type*} (n : Nat)
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (c : Comparator Decision) : Real :=
  cumulativeRegret n losses choices c

/-- The imported OCO regret view is nonnegative under round-wise comparator dominance. -/
theorem boostingRegretFromOCO_nonneg_of_le {Decision : Type*} {n : Nat}
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (c : Comparator Decision) (h : ∀ t : Fin n, losses t c.ref <= losses t (choices t)) :
    0 <= boostingRegretFromOCO n losses choices c := by
  simpa [boostingRegretFromOCO] using cumulativeRegret_nonneg_of_le losses choices c h

end MLTheory.Methods.OCO
