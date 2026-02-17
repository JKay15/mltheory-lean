/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.Bandits.Foundations
import MLTheory.Methods.RL.TemporalDifference

/-!
# MLTheory.Methods.Bandits.RLBridge

Minimal bridge between bandit regret interfaces and RL temporal-difference interfaces.
-/

namespace MLTheory.Methods.Bandits

/-- Bandit-to-RL bridge problem bundle. -/
structure BanditRLBridgeProblem (Arm : Type*) where
  bandit : BanditInstance Arm
  tdStepSize : Real

/-- Bandit scalar regret viewed as a one-step value error. -/
def banditValueGap (bestValue chosenValue : Real) : Real :=
  regret bestValue chosenValue

/-- RL TD-error proxy reused for bridge statements. -/
def tdErrorProxy (target prediction : Real) : Real :=
  MLTheory.Methods.RL.tdError target prediction

/-- Bandit value gap is definitionally TD error with
target=`bestValue`, prediction=`chosenValue`. -/
theorem banditValueGap_eq_tdErrorProxy (bestValue chosenValue : Real) :
    banditValueGap bestValue chosenValue = tdErrorProxy bestValue chosenValue := by
  rfl

/-- Bandit cumulative gap reuses shared cumulative regret. -/
def banditToRLCumulativeGap (bestValue : Real) (n : Nat) (chosenValues : Fin n -> Real) : Real :=
  cumulativeRegret bestValue n chosenValues

/-- Bridge cumulative gap is nonnegative under round-wise dominance. -/
theorem banditToRLCumulativeGap_nonneg {bestValue : Real} {n : Nat}
    (chosenValues : Fin n -> Real) (h : ∀ i : Fin n, chosenValues i <= bestValue) :
    0 <= banditToRLCumulativeGap bestValue n chosenValues := by
  simpa [banditToRLCumulativeGap] using cumulativeRegret_nonneg chosenValues h

/-- Bridge update uses the TD scalar update rule directly. -/
def banditTdUpdate (stepSize target prediction : Real) : Real :=
  MLTheory.Methods.RL.tdUpdate stepSize target prediction

/-- Bridge keeps TD error recurrence after one update step. -/
theorem banditTdError_after_update (stepSize target prediction : Real) :
    tdErrorProxy target (banditTdUpdate stepSize target prediction) =
      (1 - stepSize) * tdErrorProxy target prediction := by
  exact MLTheory.Methods.RL.tdError_after_update stepSize target prediction

end MLTheory.Methods.Bandits
