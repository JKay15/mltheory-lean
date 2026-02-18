/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.Bandits.Foundations

/-!
# MLTheory.Methods.Bandits.Stochastic

Minimal stochastic-bandit layer with UCB/ETC statement skeletons.
-/

namespace MLTheory.Methods.Bandits

/-- Stochastic bandit model with a globally optimal expected value bound. -/
structure StochasticBanditModel (Arm : Type*) where
  problem : BanditInstance Arm
  bestValue : Real
  best_upper : ∀ a : Arm, problem.rewardMean a <= bestValue

/-- UCB-style bonus term. -/
noncomputable def ucbBonus (c : Real) (round pulls : Nat) : Real :=
  c * Real.sqrt (Real.log (round + 1) / (pulls + 1))

/-- UCB score = empirical mean + bonus. -/
noncomputable def ucbScore (empiricalMean c : Real) (round pulls : Nat) : Real :=
  empiricalMean + ucbBonus c round pulls

/-- UCB bonus is nonnegative for nonnegative confidence scale. -/
theorem ucbBonus_nonneg (c : Real) (round pulls : Nat) (hc : 0 <= c) :
    0 <= ucbBonus c round pulls := by
  unfold ucbBonus
  exact mul_nonneg hc (Real.sqrt_nonneg _)

/-- UCB score lower-bounds the empirical mean under nonnegative confidence scale. -/
theorem ucbScore_ge_empiricalMean (empiricalMean c : Real) (round pulls : Nat) (hc : 0 <= c) :
    empiricalMean <= ucbScore empiricalMean c round pulls := by
  unfold ucbScore
  linarith [ucbBonus_nonneg c round pulls hc]

/-- ETC exploration budget for `numArms` arms and `explorePerArm` exploration rounds each. -/
def etcExplorationRounds (numArms explorePerArm : Nat) : Nat :=
  numArms * explorePerArm

/-- ETC exploration budget is zero when no arm is explored. -/
theorem etcExplorationRounds_zero_right (numArms : Nat) :
    etcExplorationRounds numArms 0 = 0 := by
  simp [etcExplorationRounds]

/-- Stochastic pseudo-regret reused from generic bandit cumulative regret. -/
def stochasticPseudoRegret (bestValue : Real) (n : Nat) (chosen : Fin n -> Real) : Real :=
  cumulativeRegret bestValue n chosen

/-- Pseudo-regret is nonnegative when each chosen mean is upper-bounded by best value. -/
theorem stochasticPseudoRegret_nonneg {bestValue : Real} {n : Nat} (chosen : Fin n -> Real)
    (h : ∀ i : Fin n, chosen i <= bestValue) :
    0 <= stochasticPseudoRegret bestValue n chosen := by
  simpa [stochasticPseudoRegret] using cumulativeRegret_nonneg chosen h

end MLTheory.Methods.Bandits
