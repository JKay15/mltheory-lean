/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.Bandits.Foundations

/-!
# MLTheory.Methods.Bandits.ContextualLinear

Minimal contextual-linear bandit interfaces aligned with shared regret foundations.
-/

namespace MLTheory.Methods.Bandits

/-- Contextual linear bandit problem with round-indexed contexts and realized rewards. -/
structure ContextualLinearBanditProblem (Context Arm : Type*) where
  context : Nat -> Context
  reward : Nat -> Arm -> Real

/-- Linear-style scorer over `(context, arm)` pairs. -/
structure LinearScorer (Context Arm : Type*) where
  score : Context -> Arm -> Real

/-- Predicted reward for round `t` and action `a` under a linear scorer. -/
def predictedReward {Context Arm : Type*} (problem : ContextualLinearBanditProblem Context Arm)
    (scorer : LinearScorer Context Arm) (t : Nat) (a : Arm) : Real :=
  scorer.score (problem.context t) a

/-- Optimistic score = predicted reward plus confidence bonus. -/
def optimisticScore (predicted bonus : Real) : Real :=
  predicted + bonus

/-- Optimistic score lower-bounds predicted reward when bonus is nonnegative. -/
theorem optimisticScore_ge_predicted (predicted bonus : Real) (hBonus : 0 <= bonus) :
    predicted <= optimisticScore predicted bonus := by
  unfold optimisticScore
  linarith

/-- Contextual round regret against the best available value at a round. -/
def contextualRoundRegret (bestValue chosenValue : Real) : Real :=
  regret bestValue chosenValue

/-- Contextual round regret is nonnegative under best-value dominance. -/
theorem contextualRoundRegret_nonneg_of_le {bestValue chosenValue : Real}
    (h : chosenValue <= bestValue) :
    0 <= contextualRoundRegret bestValue chosenValue := by
  exact regret_nonneg_of_le h

/-- Contextual cumulative regret hook that reuses shared cumulative regret. -/
def contextualCumulativeRegret (bestValue : Real) (n : Nat) (chosenValues : Fin n -> Real) : Real :=
  cumulativeRegret bestValue n chosenValues

/-- Contextual cumulative regret is nonnegative under round-wise dominance. -/
theorem contextualCumulativeRegret_nonneg {bestValue : Real} {n : Nat}
    (chosenValues : Fin n -> Real) (h : ∀ i : Fin n, chosenValues i <= bestValue) :
    0 <= contextualCumulativeRegret bestValue n chosenValues := by
  simpa [contextualCumulativeRegret] using cumulativeRegret_nonneg chosenValues h

/-- UCB/OFUL-style confidence radius template. -/
noncomputable def confidenceRadius (scale : Real) (round : Nat) : Real :=
  scale / Real.sqrt (round + 1)

/-- Confidence radius is nonnegative for nonnegative scale. -/
theorem confidenceRadius_nonneg (scale : Real) (round : Nat) (hScale : 0 <= scale) :
    0 <= confidenceRadius scale round := by
  unfold confidenceRadius
  have hSqrtPos : 0 < Real.sqrt (round + 1) := by
    exact Real.sqrt_pos.2 (Nat.cast_add_one_pos round)
  exact div_nonneg hScale (le_of_lt hSqrtPos)

end MLTheory.Methods.Bandits
