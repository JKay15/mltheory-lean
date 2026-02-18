/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.Bandits.Foundations

/-!
# MLTheory.Methods.Bandits.PureExplorationLinear

Minimal pure-exploration linear bandit interfaces aligned with shared regret foundations.
-/

namespace MLTheory.Methods.Bandits

/-- Pure-exploration linear bandit problem wrapper. -/
structure PureExplorationLinearProblem (Arm : Type*) where
  meanReward : Arm -> Real
  bestArm : Arm
  bestDominates : ∀ a : Arm, meanReward a <= meanReward bestArm

/-- Absolute estimation error for arm value estimates. -/
def estimationError (trueValue estimate : Real) : Real :=
  |trueValue - estimate|

/-- Estimation error is always nonnegative. -/
theorem estimationError_nonneg (trueValue estimate : Real) :
    0 <= estimationError trueValue estimate := by
  exact abs_nonneg (trueValue - estimate)

/-- Pure-exploration confidence-radius template. -/
noncomputable def confidenceRadiusPE (scale : Real) (samples : Nat) : Real :=
  scale / Real.sqrt (samples + 1)

/-- Confidence radius is nonnegative when scale is nonnegative. -/
theorem confidenceRadiusPE_nonneg (scale : Real) (samples : Nat) (hScale : 0 <= scale) :
    0 <= confidenceRadiusPE scale samples := by
  unfold confidenceRadiusPE
  have hSqrtPos : 0 < Real.sqrt (samples + 1) := by
    exact Real.sqrt_pos.2 (Nat.cast_add_one_pos samples)
  exact div_nonneg hScale (le_of_lt hSqrtPos)

/-- Pure-exploration simple regret against best value. -/
def pureExplorationSimpleRegret (bestValue recommendedValue : Real) : Real :=
  regret bestValue recommendedValue

/-- Pure-exploration simple regret is nonnegative under best-value dominance. -/
theorem pureExplorationSimpleRegret_nonneg_of_le {bestValue recommendedValue : Real}
    (h : recommendedValue <= bestValue) :
    0 <= pureExplorationSimpleRegret bestValue recommendedValue := by
  exact regret_nonneg_of_le h

/-- Fixed-confidence sample-complexity proxy. -/
def fixedConfidenceSampleComplexityPE (invGapSq logTerm : Real) : Real :=
  invGapSq * logTerm

/-- Sample-complexity proxy is nonnegative under nonnegative factors. -/
theorem fixedConfidenceSampleComplexityPE_nonneg {invGapSq logTerm : Real}
    (hGap : 0 <= invGapSq) (hLog : 0 <= logTerm) :
    0 <= fixedConfidenceSampleComplexityPE invGapSq logTerm := by
  exact mul_nonneg hGap hLog

end MLTheory.Methods.Bandits
