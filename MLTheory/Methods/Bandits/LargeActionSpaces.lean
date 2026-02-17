/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.Bandits.Foundations

/-!
# MLTheory.Methods.Bandits.LargeActionSpaces

Minimal large-action-space bandit interfaces aligned with shared regret foundations.
-/

namespace MLTheory.Methods.Bandits

/-- Large-action-space bandit problem with a finite candidate pool per round. -/
structure LargeActionBanditProblem (Arm : Type*) where
  candidatePool : Nat -> Finset Arm
  reward : Nat -> Arm -> Real

/-- Candidate-pool size at round `t`. -/
def actionPoolSize {Arm : Type*} (problem : LargeActionBanditProblem Arm) (t : Nat) : Nat :=
  (problem.candidatePool t).card

/-- Candidate-pool size is always nonnegative. -/
theorem actionPoolSize_nonneg {Arm : Type*} (problem : LargeActionBanditProblem Arm) (t : Nat) :
    0 <= actionPoolSize problem t := by
  exact Nat.zero_le _

/-- Exploration budget template proportional to pool size and per-arm probes. -/
def explorationBudget (poolSize probesPerAction : Nat) : Nat :=
  poolSize * probesPerAction

/-- Approximation gap from oracle best value to restricted candidate best value. -/
def candidateApproximationGap (oracleBest candidateBest : Real) : Real :=
  oracleBest - candidateBest

/-- Approximation gap is nonnegative when candidate best is below oracle best. -/
theorem candidateApproximationGap_nonneg_of_le {oracleBest candidateBest : Real}
    (h : candidateBest <= oracleBest) :
    0 <= candidateApproximationGap oracleBest candidateBest := by
  exact sub_nonneg.mpr h

/-- Large-action-space cumulative regret hook reusing shared cumulative regret API. -/
def largeActionCumulativeRegret (bestValue : Real) (n : Nat)
    (chosenValues : Fin n -> Real) : Real :=
  cumulativeRegret bestValue n chosenValues

/-- Large-action-space cumulative regret is nonnegative under round-wise dominance. -/
theorem largeActionCumulativeRegret_nonneg {bestValue : Real} {n : Nat}
    (chosenValues : Fin n -> Real) (h : ∀ i : Fin n, chosenValues i <= bestValue) :
    0 <= largeActionCumulativeRegret bestValue n chosenValues := by
  simpa [largeActionCumulativeRegret] using cumulativeRegret_nonneg chosenValues h

end MLTheory.Methods.Bandits
