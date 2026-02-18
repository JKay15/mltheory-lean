/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib

/-!
# MLTheory.Methods.Bandits.Foundations

Minimal bandit foundations used by stochastic/adversarial bandit modules.
-/

namespace MLTheory.Methods.Bandits

/-- Minimal stochastic bandit interface with arm-wise expected reward. -/
structure BanditInstance (Arm : Type*) where
  rewardMean : Arm -> Real

/-- One-step pseudo-regret against a reference best value. -/
def regret (bestValue chosenValue : Real) : Real := bestValue - chosenValue

/-- Regret at the best value is zero. -/
theorem regret_self (bestValue : Real) : regret bestValue bestValue = 0 := by
  simp [regret]

/-- Regret is nonnegative when chosen value does not exceed best value. -/
theorem regret_nonneg_of_le {bestValue chosenValue : Real} (h : chosenValue <= bestValue) :
    0 <= regret bestValue chosenValue := by
  exact sub_nonneg.mpr h

/-- Cumulative regret over `n` rounds with chosen values indexed by `Fin n`. -/
def cumulativeRegret (bestValue : Real) (n : Nat) (chosen : Fin n -> Real) : Real :=
  ∑ i : Fin n, regret bestValue (chosen i)

/-- Cumulative regret is nonnegative if each round's chosen value is bounded by best value. -/
theorem cumulativeRegret_nonneg {bestValue : Real} {n : Nat} (chosen : Fin n -> Real)
    (h : ∀ i : Fin n, chosen i <= bestValue) :
    0 <= cumulativeRegret bestValue n chosen := by
  unfold cumulativeRegret
  exact Finset.sum_nonneg (fun i _ => regret_nonneg_of_le (h i))

end MLTheory.Methods.Bandits
