/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.Bandits.Foundations

/-!
# MLTheory.Methods.Bandits.BestArmIdentification

Minimal best-arm-identification interfaces aligned with regret foundations.
-/

namespace MLTheory.Methods.Bandits

/-- Best-arm-identification problem wrapper. -/
structure BAIProblem (Arm : Type*) where
  problem : BanditInstance Arm
  bestArm : Arm
  bestDominates : ∀ a : Arm, problem.rewardMean a <= problem.rewardMean bestArm

/-- Simple regret of a recommended arm against the best value. -/
def simpleRegret (bestValue recommendedValue : Real) : Real :=
  regret bestValue recommendedValue

/-- Simple regret is nonnegative when the recommendation does not exceed the best value. -/
theorem simpleRegret_nonneg_of_le {bestValue recommendedValue : Real}
    (h : recommendedValue <= bestValue) :
    0 <= simpleRegret bestValue recommendedValue := by
  exact regret_nonneg_of_le h

/-- Simple regret at the best value is zero. -/
theorem simpleRegret_self (bestValue : Real) :
    simpleRegret bestValue bestValue = 0 := by
  exact regret_self bestValue

/-- BAI cumulative simple-regret hook that reuses shared cumulative-regret API. -/
def cumulativeSimpleRegret (bestValue : Real) (n : Nat)
    (recommendedValues : Fin n -> Real) : Real :=
  cumulativeRegret bestValue n recommendedValues

/-- Cumulative simple regret is nonnegative under round-wise dominance. -/
theorem cumulativeSimpleRegret_nonneg {bestValue : Real} {n : Nat}
    (recommendedValues : Fin n -> Real)
    (h : ∀ i : Fin n, recommendedValues i <= bestValue) :
    0 <= cumulativeSimpleRegret bestValue n recommendedValues := by
  simpa [cumulativeSimpleRegret] using cumulativeRegret_nonneg recommendedValues h

/-- Fixed-confidence sample-complexity template `log(1/δ)` scaled by inverse-gap square. -/
noncomputable def fixedConfidenceSampleComplexity (δ invGapSq : Real) : Real :=
  invGapSq * Real.log (1 / δ)

/-- Fixed-confidence sample complexity is nonnegative under standard assumptions. -/
theorem fixedConfidenceSampleComplexity_nonneg {δ invGapSq : Real}
    (hGap : 0 <= invGapSq) (hInv : 1 <= 1 / δ) :
    0 <= fixedConfidenceSampleComplexity δ invGapSq := by
  unfold fixedConfidenceSampleComplexity
  have hLog : 0 <= Real.log (1 / δ) := by
    exact Real.log_nonneg hInv
  exact mul_nonneg hGap hLog

end MLTheory.Methods.Bandits
